import inspect
import re
import os
import shutil
from collections import namedtuple
from pathlib import Path
from typing import Union, Tuple

import pyorient

from config.config import cmod
from stp_core.common.log import getlogger
from plenum.common.signer_did import DidSigner
from plenum.common.signer_simple import SimpleSigner
from plenum.common.constants import REQNACK, OP_FIELD_NAME
from plenum.common.types import f, HA
from stp_core.types import Identifier

from plenum.persistence.orientdb_store import OrientDbStore
from stp_core.loop.eventually import eventually
from plenum.test.test_client import genTestClient as genPlenumTestClient, \
    genTestClientProvider as genPlenumTestClientProvider
from plenum.test.test_stack import StackedTester, TestStack
from plenum.test.testable import spyable

from sovrin_common.config_util import getConfig
from sovrin_common.identity import Identity
from sovrin_common.constants import NULL
from sovrin_common.test.helper import TempStorage

from sovrin_client.client.wallet.upgrade import Upgrade
from sovrin_client.client.wallet.wallet import Wallet
from sovrin_client.client.client import Client

logger = getlogger()


class TestClientStorage(TempStorage):
    def __init__(self, name, baseDir):
        self.name = name
        self.baseDir = baseDir

    def cleanupDataLocation(self):
        self.cleanupDirectory(self.dataLocation)
        config = getConfig()
        if config.ReqReplyStore == "orientdb" or config.ClientIdentityGraph:
            try:
                self._getOrientDbStore().client.db_drop(self.name)
                logger.debug("Dropped db {}".format(self.name))
            except Exception as ex:
                logger.debug("Error while dropping db {}: {}".format(self.name,
                                                                     ex))


@spyable(methods=[Client.handleOneNodeMsg])
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
        # TODO: Why we needed following line?
        # self.cleanupDataLocation()
        super().onStopping(*args, **kwargs)


def createNym(looper, nym, creatorClient, creatorWallet: Wallet, role=None,
              verkey=None):
    idy = Identity(identifier=nym,
                   verkey=verkey,
                   role=role)
    creatorWallet.addTrustAnchoredIdentity(idy)
    reqs = creatorWallet.preparePending()
    creatorClient.submitReqs(*reqs)

    def check():
        assert creatorWallet._trustAnchored[nym].seqNo

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
    if actingWallet.getTrustAnchoredIdentity(idr):
        actingWallet.updateTrustAnchoredIdentity(idy)
    else:
        actingWallet.addTrustAnchoredIdentity(idy)
    reqs = actingWallet.preparePending()
    actingClient.submitReqs(*reqs)

    def chk():
        assert actingWallet.getTrustAnchoredIdentity(idr).seqNo is not None

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


def peer_path(filename):
    s = inspect.stack()
    caller = None
    for i in range(1, len(s)):
        # pycharm can wrap calls, so we want to ignore those in the stack
        if 'pycharm' not in s[i].filename:
            caller = s[i].filename
            break
    return Path(caller).parent.joinpath(filename)


def _within_hint(match, ctx):
    w = match.group(1)
    ctx.cmd_within = float(w) if w else None


def _ignore_extra_lines(match, ctx):
    ctx.ignore_extra_lines = True

CommandHints = namedtuple('CommandHints', 'pattern, callback')
command_hints = [
    CommandHints(r'\s*within\s*:\s*(\d*\.?\d*)', _within_hint),
    CommandHints(r'\s*ignore\s*extra\s*lines\s*', _ignore_extra_lines),
]


# marker class for regex pattern
class P(str):
    def match(self, other):
        return re.match('^{}$'.format(self), other)


class RunnerContext:
    def __init__(self):
        self.clis = {}
        self.output = []
        self.cmd_within = None
        self.line_no = 0


class ScriptRunner:
    def __init__(self, CliBuilder, looper, be, do, expect):
        self._cli_builder = CliBuilder
        self._looper = looper
        self._be = be
        self._do = do
        self._expect = expect

        # contexts allows one ScriptRunner maintain state for multiple scripts
        self._contexts = {}
        self._cur_context_name = None

        Router = namedtuple('Router', 'pattern, ends_output, handler')

        self.routers = [
            Router(re.compile(r'\s*#(.*)'), False, self._handleComment),
            Router(re.compile(r'\s*(\S*)?\s*>\s*(.*?)\s*(?:<--(.*?))?\s*'), True, self._handleCommand),
            Router(re.compile(r'\s*~\s*(be|start)\s+(.*)'), True, self._handleBe)]

    # noinspection PyAttributeOutsideInit

    def cur_ctx(self):
        try:
            return self._contexts[self._cur_context_name]
        except KeyError:
            self._contexts[self._cur_context_name] = RunnerContext()
        return self._contexts[self._cur_context_name]

    def run(self, filename, context=None):
        # by default, use a new context for each run
        self._cur_context_name = context if context else randomString()

        contents = Path(filename).read_text()

        for line in contents.lstrip().splitlines():
            self.cur_ctx().line_no += 1
            for r in self.routers:
                m = r.pattern.fullmatch(line)
                if m:
                    if r.ends_output:
                        self._checkOutput()
                    r.handler(m)
                    break
            else:
                self.cur_ctx().output.append(line)

        self._checkOutput()

    def _be_str(self, cli_str, create_if_no_exist=False):
        if cli_str not in self.cur_ctx().clis:
            if not create_if_no_exist:
                raise RuntimeError("{} does not exist; 'start' it first".
                                   format(cli_str))
            self.cur_ctx().clis[cli_str] = next(
                self._cli_builder(cli_str,
                                  looper=self._looper,
                                  unique_name=cli_str + '-' +
                                              self._cur_context_name))
        self._be(self.cur_ctx().clis[cli_str])

    def _handleBe(self, match):
        self._be_str(match.group(2), True)

    def _handleComment(self, match):
        c = match.group(1).strip()
        if c == 'break':
            pass

    def _handleCommand(self, match):
        cli_str = match.group(1)
        if cli_str:
            self._be_str(cli_str)

        cmd = match.group(2)

        hint_str = match.group(3)
        if hint_str:
            hints = hint_str.strip().split(',')
            for hint in hints:
                hint = hint.strip()
                for hint_handler in command_hints:
                    m = re.match(hint_handler.pattern, hint)
                    if m:
                        hint_handler.callback(m, self.cur_ctx())
                        break
                else:
                    raise RuntimeError("no handler found for hint '{}' at "
                                       "line no {}".
                                       format(hint, self.cur_ctx().line_no))

        self._do(cmd)

    def _checkOutput(self):
        if self.cur_ctx().output:
            new = []
            reout = re.compile(r'(.*)<--\s*regex\s*')
            for o in self.cur_ctx().output:
                m = reout.fullmatch(o)
                if m:
                    new.append(P(m.group(1).rstrip()))
                else:
                    new.append(o)

            ignore_extra_lines = False
            if hasattr(self.cur_ctx(), 'ignore_extra_lines'):
                ignore_extra_lines = self.cur_ctx().ignore_extra_lines
            self._expect(new,
                         within=self.cur_ctx().cmd_within,
                         line_no=self.cur_ctx().line_no,
                         ignore_extra_lines=ignore_extra_lines)
            self.cur_ctx().output = []
            self.cur_ctx().cmd_within = None
            self.cur_ctx().ignore_extra_lines = False
