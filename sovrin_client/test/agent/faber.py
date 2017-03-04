import os

from plenum.common.log import getlogger
from plenum.common.txn import NAME, VERSION

from anoncreds.protocol.types import AttribType, AttribDef, ID, SchemaKey
from sovrin_client.agent.agent import createAgent, runAgent, \
    isSchemaFound
from sovrin_client.agent.exception import NonceNotFound
from sovrin_client.client.client import Client
from sovrin_client.client.wallet.wallet import Wallet
from sovrin_common.config_util import getConfig
from sovrin_client.test.agent.helper import buildFaberWallet
from sovrin_client.test.agent.test_walleted_agent import TestWalletedAgent
from sovrin_client.test.helper import TestClient, primes

logger = getlogger()


class FaberAgent(TestWalletedAgent):
    def __init__(self,
                 basedirpath: str,
                 client: Client = None,
                 wallet: Wallet = None,
                 port: int = None,
                 loop=None):
        if not basedirpath:
            config = getConfig()
            basedirpath = basedirpath or os.path.expanduser(config.baseDir)

        portParam, = self.getPassedArgs()

        super().__init__('Faber College', basedirpath, client, wallet,
                         portParam or port, loop=loop)

        self.availableClaims = []

        # mapping between requester identifier and corresponding available claims
        self.requesterAvailClaims = {}

        # maps invitation nonces to internal ids
        self._invites = {
            "b1134a647eb818069c089e7694f63e6d": 1,
            "2a2eb72eca8b404e8d412c5bf79f2640": 2,
            "7513d1397e87cada4214e2a650f603eb": 3,
            "710b78be79f29fc81335abaa4ee1c5e8": 4
        }

        self._attrDef = AttribDef('faber',
                                  [AttribType('student_name', encode=True),
                                   AttribType('ssn', encode=True),
                                   AttribType('degree', encode=True),
                                   AttribType('year', encode=True),
                                   AttribType('status', encode=True)])

        # maps internal ids to attributes
        self._attrs = {
            1: self._attrDef.attribs(
                student_name="Alice Garcia",
                ssn="123-45-6789",
                degree="Bachelor of Science, Marketing",
                year="2015",
                status="graduated"),
            2: self._attrDef.attribs(
                student_name="Carol Atkinson",
                ssn="783-41-2695",
                degree="Bachelor of Science, Physics",
                year="2012",
                status="graduated"),
            3: self._attrDef.attribs(
                student_name="Frank Jeffrey",
                ssn="996-54-1211",
                degree="Bachelor of Arts, History",
                year="2013",
                status="dropped"),
            4: self._attrDef.attribs(
                student_name="Craig Richards",
                ssn="151-44-5876",
                degree="MBA, Finance",
                year="2015",
                status="graduated")
        }

        self._schema = SchemaKey("Transcript", "1.2", self.wallet.defaultId)

    def getInternalIdByInvitedNonce(self, nonce):
        if nonce in self._invites:
            return self._invites[nonce]
        else:
            raise NonceNotFound

    def isClaimAvailable(self, link, claimName):
        return claimName == "Transcript"

    def getAvailableClaimList(self, requesterId):
        return self.availableClaims + \
               self.requesterAvailClaims.get(requesterId, [])

    async def postClaimVerif(self, claimName, link, frm):
        pass

    async def initAvailableClaimList(self):
        schema = await self.issuer.wallet.getSchema(ID(self._schema))
        self.availableClaims.append({
            NAME: schema.name,
            VERSION: schema.version,
            "schemaSeqNo": schema.seqId
        })

    def _addAtrribute(self, schemaKey, proverId, link):
        attr = self._attrs[self.getInternalIdByInvitedNonce(proverId)]
        self.issuer._attrRepo.addAttributes(schemaKey=schemaKey,
                                            userId=proverId,
                                            attributes=attr)

    async def addSchemasToWallet(self):
        schema = await self.issuer.genSchema(self._schema.name,
                                             self._schema.version,
                                             self._attrDef.attribNames(),
                                             'CL')
        if schema:
            schemaId = ID(schemaKey=schema.getKey(), schemaId=schema.seqId)
            p_prime, q_prime = primes["prime2"]
            await self.issuer.genKeys(schemaId, p_prime=p_prime, q_prime=q_prime)
            await self.issuer.issueAccumulator(schemaId=schemaId, iA='110', L=5)
            await self.initAvailableClaimList()
        return schema

    async def bootstrap(self):
        ranViaScript = False
        if __name__ == "__main__":
            ranViaScript = True
        isSchemaFound(await self.addSchemasToWallet(), ranViaScript)


def createFaber(name=None, wallet=None, basedirpath=None, port=None):
    return createAgent(FaberAgent, name or "Faber College",
                       wallet or buildFaberWallet(),
                       basedirpath, port, clientClass=TestClient)

if __name__ == "__main__":
    faber = createFaber(port=5555)
    runAgent(faber)
