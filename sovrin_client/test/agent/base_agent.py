import os

from ioflo.base.consoling import Console

from plenum.common.log import Logger, getlogger
from sovrin_client.agent.agent import runBootstrap

from sovrin_client.test.agent.test_walleted_agent import TestWalletedAgent

from plenum.common.txn import NAME, VERSION

from anoncreds.protocol.types import ID
from sovrin_client.agent.exception import NonceNotFound
from sovrin_client.client.client import Client
from sovrin_client.client.wallet.wallet import Wallet
from sovrin_client.test.helper import primes
from sovrin_common.config import agentLoggingLevel
from sovrin_common.config_util import getConfig


class BaseAgent(TestWalletedAgent):
    def __init__(self,
                 name: str,
                 basedirpath: str,
                 client: Client = None,
                 wallet: Wallet = None,
                 port: int = None,
                 loop=None):

        if not basedirpath:
            config = getConfig()
            basedirpath = basedirpath or os.path.expanduser(config.baseDir)

        portParam, = self.getPassedArgs()
        super().__init__(name, basedirpath, client, wallet,
                         portParam or port, loop=loop)

        self.logger = getlogger()

        # available claims to anyone who interacts with this agent
        self.availableClaimsToAll = []

        # available claims only for certain individual (by nonce)
        self.availableClaimsByNonce = {}

        # mapping between specific identifier and available claims which would
        # have been available once they have requested information (proof etc).
        self.availableClaimsByIdentifier = {}

        self._invites = {}

    def setupLogging(self, filePath):
        Logger().setLogLevel(agentLoggingLevel)
        Logger().enableFileLogging(filePath)
        self.setupRaetLogging(Console.Wordage.concise)

    def setupRaetLogging(self, level):
        Logger().setupRaet(raet_log_level=level)

    def getInternalIdByInvitedNonce(self, nonce):
        if nonce in self._invites:
            return self._invites[nonce]
        else:
            raise NonceNotFound

    def getAvailableClaimList(self, nonce, requesterId):
        assert nonce
        assert requesterId
        return self.availableClaimsToAll + \
               self.availableClaimsByNonce.get(nonce, []) + \
               self.availableClaimsByIdentifier.get(requesterId, [])

    def isClaimAvailable(self, link, claimName):
        return claimName in self.getAvailableClaimList(link.invitationNonce,
                                                       link.localIdentifier)

    def getSchemaKeysToBeGenerated(self):
        raise NotImplemented

    def getSchemaKeysForClaimsAvailableToAll(self):
        return self.getSchemaKeysToBeGenerated()

    def getSchemaKeysForClaimsAvailableToSpecificNonce(self):
        return {}

    async def postClaimVerif(self, claimName, link, frm):
        pass

    async def initAvailableClaimList(self):
        for schemaKey in self.getSchemaKeysForClaimsAvailableToAll():
            schema = await self.issuer.wallet.getSchema(ID(schemaKey))
            self.availableClaimsToAll.append({
                NAME: schema.name,
                VERSION: schema.version,
                "schemaSeqNo": schema.seqId
            })
        for nonce, schemaKey in self.getSchemaKeysForClaimsAvailableToSpecificNonce():
            schema = await self.issuer.wallet.getSchema(ID(schemaKey))
            self.availableClaimsByNonce[nonce] = {
                NAME: schema.name,
                VERSION: schema.version,
                "schemaSeqNo": schema.seqId
            }

    def _addAttribute(self, schemaKey, proverId, link):
        attr = self._attrs[self.getInternalIdByInvitedNonce(proverId)]
        self.issuer._attrRepo.addAttributes(schemaKey=schemaKey,
                                            userId=proverId,
                                            attributes=attr)

    async def addSchemasToWallet(self):
        for schemaKey in self.getSchemaKeysToBeGenerated():
            schema = await self.issuer.genSchema(schemaKey.name,
                                                 schemaKey.version,
                                                 self._attrDef.attribNames(),
                                                 'CL')
            if schema:
                schemaId = ID(schemaKey=schema.getKey(), schemaId=schema.seqId)
                p_prime, q_prime = primes["prime2"]
                await self.issuer.genKeys(schemaId, p_prime=p_prime, q_prime=q_prime)
                await self.issuer.issueAccumulator(schemaId=schemaId, iA='110', L=5)

        await self.initAvailableClaimList()

    async def bootstrap(self):
        await runBootstrap(self.addSchemasToWallet)


