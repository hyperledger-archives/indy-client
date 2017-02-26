import os
import shutil

import pyorient
from plenum.common.log import getlogger
from plenum.common.looper import Looper
from plenum.common.signer_did import DidSigner
from plenum.common.signer_simple import SimpleSigner
from plenum.common.txn import REQNACK
from plenum.common.types import OP_FIELD_NAME, f
from plenum.persistence.orientdb_store import OrientDbStore
from plenum.common.eventually import eventually
from plenum.test.helper import initDirWithGenesisTxns
from plenum.test.test_stack import StackedTester, TestStack
from plenum.test.testable import Spyable
from plenum.test.cli.helper import newCLI as newPlenumCLI

from sovrin_client.client.wallet.upgrade import Upgrade
from sovrin_client.client.wallet.wallet import Wallet
from sovrin_client.test.cli.helper import TestCLI
from sovrin_common.config_util import getConfig
from sovrin_common.constants import Environment
from sovrin_common.identity import Identity

from sovrin_client.client.client import Client
from sovrin_common.txn import NULL
from sovrin_node.test.helper import TestNode, genTestClient

logger = getlogger()


class TestClientStorage:
    def __init__(self, name, baseDir):
        self.name = name
        self.baseDir = baseDir

    def cleanupDataLocation(self):
        loc = os.path.join(self.baseDir, "data/clients", self.name)
        logger.debug('Cleaning up location {} of test client {}'.
                     format(loc, self.name))
        try:
            shutil.rmtree(loc)
        except Exception as ex:
            logger.debug("Error while removing temporary directory {}".format(
                ex))
        config = getConfig()
        if config.ReqReplyStore == "orientdb" or config.ClientIdentityGraph:
            try:
                self._getOrientDbStore().client.db_drop(self.name)
                logger.debug("Dropped db {}".format(self.name))
            except Exception as ex:
                logger.debug("Error while dropping db {}: {}".format(self.name,
                                                                     ex))


@Spyable(methods=[Client.handleOneNodeMsg])
class TestClient(Client, StackedTester, TestClientStorage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        TestClientStorage.__init__(self, self.name, self.basedirpath)

    @staticmethod
    def stackType():
        return TestStack

    def _getOrientDbStore(self):
        config = getConfig()
        return OrientDbStore(user=config.OrientDB["user"],
                             password=config.OrientDB["password"],
                             dbName=self.name,
                             storageType=pyorient.STORAGE_TYPE_MEMORY)

    def onStopping(self, *args, **kwargs):
        self.cleanupDataLocation()
        super().onStopping(*args, **kwargs)


def createNym(looper, nym, creatorClient, creatorWallet: Wallet, role=None,
              verkey=None):
    idy = Identity(identifier=nym,
                   verkey=verkey,
                   role=role)
    creatorWallet.addSponsoredIdentity(idy)
    reqs = creatorWallet.preparePending()
    creatorClient.submitReqs(*reqs)

    def check():
        assert creatorWallet._sponsored[nym].seqNo

    looper.run(eventually(check, retryWait=1, timeout=10))


def makePendingTxnsRequest(client, wallet):
    wallet.pendSyncRequests()
    prepared = wallet.preparePending()
    client.submitReqs(*prepared)


def buildStewardClient(looper, tdir, stewardWallet):
    s, _ = genTestClient(tmpdir=tdir, usePoolLedger=True)
    s.registerObserver(stewardWallet.handleIncomingReply)
    looper.add(s)
    looper.run(s.ensureConnectedToNodes())
    makePendingTxnsRequest(s, stewardWallet)
    return s


def newCLI(looper, tdir, subDirectory=None, conf=None, poolDir=None,
           domainDir=None, multiPoolNodes=None, unique_name=None):
    tempDir = os.path.join(tdir, subDirectory) if subDirectory else tdir
    if poolDir or domainDir:
        initDirWithGenesisTxns(tempDir, conf, poolDir, domainDir)

    if multiPoolNodes:
        conf.ENVS = {}
        for pool in multiPoolNodes:
            conf.poolTransactionsFile = "pool_transactions_{}".format(pool.name)
            conf.domainTransactionsFile = "transactions_{}".format(pool.name)
            conf.ENVS[pool.name] = \
                Environment("pool_transactions_{}".format(pool.name),
                                "transactions_{}".format(pool.name))
            initDirWithGenesisTxns(
                tempDir, conf, os.path.join(pool.tdirWithPoolTxns, pool.name),
                os.path.join(pool.tdirWithDomainTxns, pool.name))

    return newPlenumCLI(looper, tempDir, cliClass=TestCLI,
                        nodeClass=TestNode, clientClass=TestClient, config=conf,
                        unique_name=unique_name)


def getCliBuilder(tdir, tconf, tdirWithPoolTxns, tdirWithDomainTxns,
                  multiPoolNodes=None):
    def _(subdir, looper=None, unique_name=None):
        def new():
            return newCLI(looper,
                          tdir,
                          subDirectory=subdir,
                          conf=tconf,
                          poolDir=tdirWithPoolTxns,
                          domainDir=tdirWithDomainTxns,
                          multiPoolNodes=multiPoolNodes,
                          unique_name=unique_name)
        if looper:
            yield new()
        else:
            with Looper(debug=False) as looper:
                yield new()
    return _


def addRole(looper, creatorClient, creatorWallet, name, useDid=True,
            addVerkey=True, role=None):
    wallet = Wallet(name)
    signer = DidSigner() if useDid else SimpleSigner()
    idr, _ = wallet.addIdentifier(signer=signer)
    verkey = wallet.getVerkey(idr) if addVerkey else None
    createNym(looper, idr, creatorClient, creatorWallet, verkey=verkey,
              role=role)
    return wallet


def suspendRole(looper, actingClient, actingWallet, did):
    idy = Identity(identifier=did, role=NULL)
    return makeIdentityRequest(looper, actingClient, actingWallet, idy)


def changeVerkey(looper, actingClient, actingWallet, idr, verkey):
    idy = Identity(identifier=idr,
                   verkey=verkey)
    return makeIdentityRequest(looper, actingClient, actingWallet, idy)


def submitPoolUpgrade(looper, senderClient, senderWallet, name, action, version,
                      schedule, timeout, sha256):
    upgrade = Upgrade(name, action, schedule, version, sha256, timeout,
                      senderWallet.defaultId)
    senderWallet.doPoolUpgrade(upgrade)
    reqs = senderWallet.preparePending()
    senderClient.submitReqs(*reqs)

    def check():
        assert senderWallet._upgrades[upgrade.key].seqNo

    looper.run(eventually(check, timeout=4))


def getClientAddedWithRole(nodeSet, tdir, looper, client, wallet, name, role):
    newWallet = addRole(looper, client, wallet, name=name, role=role)
    c, _ = genTestClient(nodeSet, tmpdir=tdir, usePoolLedger=True)
    looper.add(c)
    looper.run(c.ensureConnectedToNodes())
    c.registerObserver(newWallet.handleIncomingReply)
    return c, newWallet


def checkNacks(client, reqId, contains='', nodeCount=4):
    logger.debug("looking for :{}".format(reqId))
    reqs = [x for x, _ in client.inBox if x[OP_FIELD_NAME] == REQNACK and
            x[f.REQ_ID.nm] == reqId]
    for r in reqs:
        logger.debug("printing r :{}".format(r))
        assert f.REASON.nm in r
        assert contains in r[f.REASON.nm], '{} not in {}'.format(contains,
                                                                 r[f.REASON.nm])
    assert len(reqs) == nodeCount


def submitAndCheckNacks(looper, client, wallet, op, identifier,
                        contains='UnauthorizedClientRequest'):
    req = wallet.signOp(op, identifier=identifier)
    wallet.pendRequest(req)
    reqs = wallet.preparePending()
    client.submitReqs(*reqs)
    looper.run(eventually(checkNacks,
                          client,
                          req.reqId,
                          contains, retryWait=1, timeout=15))


def makeIdentityRequest(looper, actingClient, actingWallet, idy):
    idr = idy.identifier
    if actingWallet.getSponsoredIdentity(idr):
        actingWallet.updateSponsoredIdentity(idy)
    else:
        actingWallet.addSponsoredIdentity(idy)
    reqs = actingWallet.preparePending()
    actingClient.submitReqs(*reqs)

    def chk():
        assert actingWallet.getSponsoredIdentity(idr).seqNo is not None

    looper.run(eventually(chk, retryWait=1, timeout=5))
    return reqs
