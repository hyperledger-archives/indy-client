import os
import shutil
from typing import Union, Tuple

import pyorient

from config.config import cmod
from plenum.common.log import getlogger
from plenum.common.looper import Looper
from plenum.common.signer_did import DidSigner
from plenum.common.signer_simple import SimpleSigner
from plenum.common.txn import REQNACK
from plenum.common.types import OP_FIELD_NAME, f, Identifier, HA
from plenum.persistence.orientdb_store import OrientDbStore
from plenum.common.eventually import eventually
from plenum.test.helper import initDirWithGenesisTxns
from plenum.test.test_client import genTestClient as genPlenumTestClient, \
    genTestClientProvider as genPlenumTestClientProvider
from plenum.test.test_stack import StackedTester, TestStack
from plenum.test.testable import Spyable
from plenum.test.cli.helper import newCLI as newPlenumCLI

from sovrin_client.client.wallet.upgrade import Upgrade
from sovrin_client.client.wallet.wallet import Wallet
from sovrin_common.config_util import getConfig
from sovrin_common.constants import Environment
from sovrin_common.identity import Identity

from sovrin_client.client.client import Client
from sovrin_common.txn import NULL

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


# def newCLI(looper, tdir, subDirectory=None, conf=None, poolDir=None,
#            domainDir=None, multiPoolNodes=None, unique_name=None):
#     tempDir = os.path.join(tdir, subDirectory) if subDirectory else tdir
#     if poolDir or domainDir:
#         initDirWithGenesisTxns(tempDir, conf, poolDir, domainDir)
#
#     if multiPoolNodes:
#         conf.ENVS = {}
#         for pool in multiPoolNodes:
#             conf.poolTransactionsFile = "pool_transactions_{}".format(pool.name)
#             conf.domainTransactionsFile = "transactions_{}".format(pool.name)
#             conf.ENVS[pool.name] = \
#                 Environment("pool_transactions_{}".format(pool.name),
#                                 "transactions_{}".format(pool.name))
#             initDirWithGenesisTxns(
#                 tempDir, conf, os.path.join(pool.tdirWithPoolTxns, pool.name),
#                 os.path.join(pool.tdirWithDomainTxns, pool.name))
#
#     from sovrin_node.test.helper import TestNode
#     return newPlenumCLI(looper, tempDir, cliClass=TestCLI,
#                         nodeClass=TestNode, clientClass=TestClient, config=conf,
#                         unique_name=unique_name)
#
#
# def getCliBuilder(tdir, tconf, tdirWithPoolTxns, tdirWithDomainTxns,
#                   multiPoolNodes=None):
#     def _(subdir, looper=None, unique_name=None):
#         def new():
#             return newCLI(looper,
#                           tdir,
#                           subDirectory=subdir,
#                           conf=tconf,
#                           poolDir=tdirWithPoolTxns,
#                           domainDir=tdirWithDomainTxns,
#                           multiPoolNodes=multiPoolNodes,
#                           unique_name=unique_name)
#         if looper:
#             yield new()
#         else:
#             with Looper(debug=False) as looper:
#                 yield new()
#     return _


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


primes = {
    "prime1":
        (cmod.integer(
            157329491389375793912190594961134932804032426403110797476730107804356484516061051345332763141806005838436304922612495876180233509449197495032194146432047460167589034147716097417880503952139805241591622353828629383332869425029086898452227895418829799945650973848983901459733426212735979668835984691928193677469),
         cmod.integer(
             151323892648373196579515752826519683836764873607632072057591837216698622729557534035138587276594156320800768525825023728398410073692081011811496168877166664537052088207068061172594879398773872352920912390983199416927388688319207946493810449203702100559271439586753256728900713990097168484829574000438573295723))
    , "prime2":
        (cmod.integer(
            150619677884468353208058156632953891431975271416620955614548039937246769610622017033385394658879484186852231469238992217246264205570458379437126692055331206248530723117202131739966737760399755490935589223401123762051823602343810554978803032803606907761937587101969193241921351011430750970746500680609001799529),
         cmod.integer(
             171590857568436644992359347719703764048501078398666061921719064395827496970696879481740311141148273607392657321103691543916274965279072000206208571551864201305434022165176563363954921183576230072812635744629337290242954699427160362586102068962285076213200828451838142959637006048439307273563604553818326766703))
}


def genTestClient(nodes = None,
                  nodeReg=None,
                  tmpdir=None,
                  identifier: Identifier = None,
                  verkey: str = None,
                  peerHA: Union[HA, Tuple[str, int]] = None,
                  testClientClass=TestClient,
                  usePoolLedger=False,
                  name: str=None) -> (TestClient, Wallet):
    testClient, wallet = genPlenumTestClient(nodes,
                                             nodeReg,
                                             tmpdir,
                                             testClientClass,
                                             verkey=verkey,
                                             identifier=identifier,
                                             bootstrapKeys=False,
                                             usePoolLedger=usePoolLedger,
                                             name=name)
    testClient.peerHA = peerHA
    return testClient, wallet


def genConnectedTestClient(looper,
                           nodes = None,
                           nodeReg=None,
                           tmpdir=None,
                           identifier: Identifier = None,
                           verkey: str = None
                           ) -> TestClient:
    c, w = genTestClient(nodes, nodeReg=nodeReg, tmpdir=tmpdir,
                         identifier=identifier, verkey=verkey)
    looper.add(c)
    looper.run(c.ensureConnectedToNodes())
    return c, w


def genTestClientProvider(nodes = None,
                          nodeReg=None,
                          tmpdir=None,
                          clientGnr=genTestClient):
    return genPlenumTestClientProvider(nodes, nodeReg, tmpdir, clientGnr)


def clientFromSigner(signer, looper, nodeSet, tdir):
    wallet = Wallet(signer.identifier)
    wallet.addIdentifier(signer)
    s = genTestClient(nodeSet, tmpdir=tdir, identifier=signer.identifier)
    looper.add(s)
    looper.run(s.ensureConnectedToNodes())
    return s


def addUser(looper, creatorClient, creatorWallet, name, useDid=True,
            addVerkey=True):
    wallet = Wallet(name)
    signer = DidSigner() if useDid else SimpleSigner()
    idr, _ = wallet.addIdentifier(signer=signer)
    verkey = wallet.getVerkey(idr) if addVerkey else None
    createNym(looper, idr, creatorClient, creatorWallet, verkey=verkey)
    return wallet