import asyncio
import os

from typing import Dict
from typing import Tuple

import errno

from anoncreds.protocol.repo.attributes_repo import AttributeRepoInMemory
from plenum.common.signer_simple import SimpleSigner
from plenum.common.exceptions import NoConsensusYet
from stp_core.common.log import getlogger
from stp_core.loop.looper import Looper
from plenum.common.motor import Motor
from plenum.common.startable import Status
from plenum.common.types import HA
from plenum.common.util import saveGivenWallet, normalizedWalletFileName, getLastSavedWalletFileName, \
    getWalletByPath
from stp_core.types import Identifier
from stp_core.network.util import checkPortAvailable
from sovrin_client.agent.agent_net import AgentNet
from sovrin_client.agent.caching import Caching
from sovrin_client.agent.walleted import Walleted
from sovrin_client.anon_creds.sovrin_issuer import SovrinIssuer
from sovrin_client.anon_creds.sovrin_prover import SovrinProver
from sovrin_client.anon_creds.sovrin_verifier import SovrinVerifier
from sovrin_client.client.client import Client
from sovrin_client.client.wallet.wallet import Wallet
from sovrin_common.config import agentLoggingLevel
from sovrin_common.config_util import getConfig
from sovrin_common.identity import Identity
from sovrin_common.strict_types import strict_types, decClassMethods
from stp_core.network.port_dispenser import genHa
from plenum.common.util import randomString

logger = getlogger()
logger.setLevel(agentLoggingLevel)


@decClassMethods(strict_types())
class Agent(Motor, AgentNet):
    def __init__(self,
                 name: str=None,
                 basedirpath: str=None,
                 client: Client=None,
                 port: int=None,
                 loop=None,
                 config=None,
                 endpointArgs=None):

        self.endpoint = None
        if port:
            checkPortAvailable(HA("0.0.0.0", port))
        Motor.__init__(self)
        self.loop = loop or asyncio.get_event_loop()
        self._eventListeners = {}  # Dict[str, set(Callable)]
        self._name = name or 'Agent'
        self._port = port

        self.config = config or getConfig()
        self.basedirpath = basedirpath or os.path.expanduser(self.config.baseDir)
        self.endpointArgs = endpointArgs

        # Client used to connect to Sovrin and forward on owner's txns
        self._client = client  # type: Client

        # known identifiers of this agent's owner
        self.ownerIdentifiers = {}  # type: Dict[Identifier, Identity]

    @property
    def client(self):
        return self._client

    @client.setter
    def client(self, client):
        self._client = client

    @property
    def name(self):
        return self._name

    @property
    def port(self):
        return self._port

    async def prod(self, limit) -> int:
        c = 0
        if self.get_status() == Status.starting:
            self.status = Status.started
            c += 1
        if self.client:
            c += await self.client.prod(limit)
        if self.endpoint:
            c += await self.endpoint.service(limit)
        return c

    def start(self, loop):
        AgentNet.__init__(self,
                          name=self._name.replace(" ", ""),
                          port=self._port,
                          basedirpath=self.basedirpath,
                          msgHandler=self.handleEndpointMessage,
                          config = self.config,
                          endpointArgs=self.endpointArgs)



        super().start(loop)
        if self.client:
            self.client.start(loop)
        if self.endpoint:
            self.endpoint.start()

    def stop(self, *args, **kwargs):
        super().stop(*args, **kwargs)
        if self.client:
            self.client.stop()
        if self.endpoint:
            self.endpoint.stop()

    def _statusChanged(self, old, new):
        pass

    def onStopping(self, *args, **kwargs):
        pass

    def connect(self, network: str):
        """
        Uses the client to connect to Sovrin
        :param network: (test|live)
        :return:
        """
        raise NotImplementedError

    def syncKeys(self):
        """
        Iterates through ownerIdentifiers and ensures the keys are correct
        according to Sovrin. Updates the updated
        :return:
        """
        raise NotImplementedError

    def handleOwnerRequest(self, request):
        """
        Consumes an owner request, verifies it's authentic (by checking against
        synced owner identifiers' keys), and handles it.
        :param request:
        :return:
        """
        raise NotImplementedError

    def handleEndpointMessage(self, msg):
        raise NotImplementedError

    def ensureConnectedToDest(self, name, ha, clbk, *args):
        if self.endpoint.isConnectedTo(name=name, ha=ha):
            if clbk:
                clbk(*args)
        else:
            self.loop.call_later(.2, self.ensureConnectedToDest,
                                 name, ha, clbk, *args)

    def sendMessage(self, msg, name: str = None, ha: Tuple = None):

        def _send(msg):
            nonlocal name, ha
            self.endpoint.send(msg, name, ha)
            logger.debug("Message sent (to -> {}): {}".format(ha, msg))

        # TODO: if we call following isConnectedTo method by ha,
        # there was a case it found more than one remote, so for now,
        # I have changed it to call by remote name (which I am not sure
        # fixes the issue), need to come back to this.
        if not self.endpoint.isConnectedTo(name=name, ha=ha):
            self.ensureConnectedToDest(name, ha, _send, msg)
        else:
            _send(msg)

    def registerEventListener(self, eventName, listener):
        cur = self._eventListeners.get(eventName)
        if cur:
            self._eventListeners[eventName] = cur.add(listener)
        else:
            self._eventListeners[eventName] = {listener}

    def deregisterEventListener(self, eventName, listener):
        cur = self._eventListeners.get(eventName)
        if cur:
            self._eventListeners[eventName] = cur - set(listener)


class WalletedAgent(Walleted, Agent, Caching):
    def __init__(self,
                 name: str,
                 basedirpath: str,
                 client: Client = None,
                 wallet: Wallet = None,
                 port: int = None,
                 loop=None,
                 attrRepo=None,
                 config=None,
                 endpointArgs=None):

        Agent.__init__(self, name, basedirpath, client, port, loop=loop,
                       config=config, endpointArgs=endpointArgs)

        self.config = getConfig(basedirpath)

        self._wallet = None

        # restore any active wallet belonging to this agent
        self._restoreWallet()

        # if no persisted wallet is restored and a wallet is passed,
        # then use given wallet, else ignore the given wallet
        if not self.wallet and wallet:
            self.wallet = wallet

        # if wallet is not yet set, then create a wallet
        if not self.wallet:
            self.wallet = Wallet(name)

        self._attrRepo = attrRepo or AttributeRepoInMemory()

        Walleted.__init__(self)

        if self.client:
            self._initIssuerProverVerifier()

        self._restoreIssuerWallet()

    def _initIssuerProverVerifier(self):
        self.issuer = SovrinIssuer(client=self.client, wallet=self._wallet,
                                   attrRepo=self._attrRepo)
        self.prover = SovrinProver(client=self.client, wallet=self._wallet)
        self.verifier = SovrinVerifier(client=self.client, wallet=self._wallet)

    @property
    def wallet(self):
        return self._wallet

    @wallet.setter
    def wallet(self, newWallet):
        self._wallet = newWallet

    @Agent.client.setter
    def client(self, client):
        Agent.client.fset(self, client)
        if self.client:
            self._initIssuerProverVerifier()

    def start(self, loop):
        super().start(loop)

    def stop(self, *args, **kwargs):
        self._saveAllWallets()
        super().stop(*args, **kwargs)

    def getContextDir(self):
        return os.path.expanduser(os.path.join(
            self.config.baseDir, self.config.keyringsDir, "agents",
            self.name.lower().replace(" ", "-")))

    def _getIssuerWalletContextDir(self):
        return os.path.join(self.getContextDir(), "issuer")

    def _saveAllWallets(self):
        self._saveWallet(self._wallet, self.getContextDir())
        self._saveIssuerWallet()
        # TODO: There are some other wallets for prover and verifier,
        # which we may also have to persist/restore as need arises

    def _saveIssuerWallet(self):
        if self.issuer:
            self.issuer.prepareForWalletPersistence()
            self._saveWallet(self.issuer.wallet, self._getIssuerWalletContextDir(),
                     walletName="issuer")

    def _saveWallet(self, wallet: Wallet, contextDir, walletName=None):
        try:
            walletName = walletName or wallet.name
            fileName = normalizedWalletFileName(walletName)
            walletFilePath = saveGivenWallet(wallet, fileName, contextDir)
            self.logger.info('Active keyring "{}" saved ({})'.
                             format(walletName, walletFilePath))
        except IOError as ex:
            self.logger.info("Error occurred while saving wallet. " +
                             "error no.{}, error.{}"
                             .format(ex.errno, ex.strerror))

    def _restoreWallet(self):
        restoredWallet, walletFilePath = self._restoreLastActiveWallet(
            self.getContextDir())
        if restoredWallet:
            self.wallet = restoredWallet
            self.logger.info('Saved keyring "{}" restored ({})'.
                             format(self.wallet.name, walletFilePath))

    def _restoreIssuerWallet(self):
        if self.issuer:
            restoredWallet, walletFilePath = self._restoreLastActiveWallet(
                self._getIssuerWalletContextDir())
            if restoredWallet:
                self.issuer.restorePersistedWallet(restoredWallet)
                self.logger.info('Saved keyring "issuer" restored ({})'.
                             format(walletFilePath))

    def _restoreLastActiveWallet(self, contextDir):
        walletFilePath = None
        try:
            walletFileName = getLastSavedWalletFileName(contextDir)
            walletFilePath = os.path.join(contextDir, walletFileName)
            wallet = getWalletByPath(walletFilePath)
            # TODO: What about current wallet if any?
            return wallet, walletFilePath
        except ValueError as e:
            if not str(e) == "max() arg is an empty sequence":
                self.logger.info("No wallet to restore")
        except (ValueError, AttributeError) as e:
            self.logger.info(
                "error occurred while restoring wallet {}: {}".
                    format(walletFilePath, e))
        except IOError as exc:
            if exc.errno == errno.ENOENT:
                self.logger.debug("no such keyring file exists ({})".
                              format(walletFilePath))
            else:
                raise exc
        return None, None


def createAgent(agentClass, name, wallet=None, basedirpath=None, port=None,
                loop=None, clientClass=Client):
    config = getConfig()

    if not wallet:
        wallet = Wallet(name)
        wallet.addIdentifier(signer=SimpleSigner(
            seed=randomString(32).encode('utf-8')))
    if not basedirpath:
        basedirpath = config.baseDir
    if not port:
        _, port = genHa()

    _, clientPort = genHa()

    client = clientClass(randomString(6),
                         ha=("0.0.0.0", clientPort),
                         basedirpath=basedirpath)

    return agentClass(basedirpath=basedirpath,
                      client=client,
                      wallet=wallet,
                      port=port,
                      loop=loop)


def runAgent(agent, looper=None, bootstrap=True):
    assert agent

    def doRun(looper):
        looper.add(agent)
        logger.debug("Running {} now (port: {})".format(agent.name, agent.port))
        if bootstrap:
            looper.run(agent.bootstrap())

    if looper:
        doRun(looper)
    else:
        with Looper(debug=True, loop=agent.loop) as looper:
            doRun(looper)
            looper.run()


async def runBootstrap(bootstrapFunc):
    try:
        await bootstrapFunc()
    except TimeoutError as exc:
        raise NoConsensusYet("consensus is not yet achieved, "
                             "check if sovrin is running and "
                             "client is able to connect to it") from exc
