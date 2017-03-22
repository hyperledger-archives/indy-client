from plenum.common.log import getlogger
from plenum.common.constants import NAME, VERSION

from anoncreds.protocol.types import AttribType, AttribDef, SchemaKey, \
    ID
from sovrin_client.agent.agent import createAgent
from sovrin_client.client.client import Client
from sovrin_client.client.wallet.wallet import Wallet
from sovrin_client.test.agent.base_agent import BaseAgent
from sovrin_client.test.agent.helper import buildAcmeWallet
from sovrin_client.test.agent.test_walleted_agent import TestWalletedAgent
from sovrin_client.test.helper import TestClient

logger = getlogger()


class AcmeAgent(BaseAgent):
    def __init__(self,
                 basedirpath: str,
                 client: Client = None,
                 wallet: Wallet = None,
                 port: int = None,
                 loop=None):

        portParam, = self.getPassedArgs()

        super().__init__('Acme Corp', basedirpath, client, wallet,
                         portParam or port, loop=loop)

        # maps invitation nonces to internal ids
        self._invites = {
            "57fbf9dc8c8e6acde33de98c6d747b28c": 1,
            "3a2eb72eca8b404e8d412c5bf79f2640": 2,
            "8513d1397e87cada4214e2a650f603eb": 3,
            "810b78be79f29fc81335abaa4ee1c5e8": 4
        }

        self._attrDefJobCert = AttribDef('Job-Certificate',
                  [AttribType('first_name', encode=True),
                   AttribType('last_name', encode=True),
                   AttribType('employee_status', encode=True),
                   AttribType('experience', encode=True),
                   AttribType('salary_bracket', encode=True)])

        self._attrDefJobApp = AttribDef('Job-Application',
                      [AttribType('first_name', encode=True),
                       AttribType('last_name', encode=True),
                       AttribType('phone_number', encode=True),
                       AttribType('degree', encode=True),
                       AttribType('status', encode=True),
                       AttribType('ssn', encode=True)])

        # maps internal ids to attributes
        self._attrs = {
            1: self._attrDefJobCert.attribs(
                first_name="Alice",
                last_name="Garcia",
                employee_status="Permanent",
                experience="3 years",
                salary_bracket="between $50,000 to $100,000"),
            2: self._attrDefJobCert.attribs(
                first_name="Carol",
                last_name="Atkinson",
                employee_status="Permanent",
                experience="2 years",
                salary_bracket="between $60,000 to $90,000"),
            3: self._attrDefJobCert.attribs(
                first_name="Frank",
                last_name="Jeffrey",
                employee_status="Temporary",
                experience="4 years",
                salary_bracket="between $40,000 to $80,000"),
            4: self._attrDefJobCert.attribs(
                first_name="Craig",
                last_name="Richards",
                employee_status="On Contract",
                experience="3 years",
                salary_bracket="between $50,000 to $70,000")
        }

    def getAttrDefs(self):
        return [self._attrDefJobCert, self._attrDefJobApp]

    def getAttrs(self):
        return self._attrs

    def getSchemaKeysToBeGenerated(self):
        return [SchemaKey("Job-Certificate", "0.2",
                          self.wallet.defaultId),
                SchemaKey("Job-Application", "0.2",
                          self.wallet.defaultId)]

    def getSchemaKeysForClaimsAvailableToAll(self):
        return []

    async def postClaimVerif(self, claimName, link, frm):
        nac = await self.newAvailableClaimsPostClaimVerif(claimName)
        oldClaims = self.availableClaimsByIdentifier.get(link.remoteIdentifier)
        if not oldClaims:
            oldClaims = []
        oldClaims.extend(nac)
        self.availableClaimsByIdentifier[link.remoteIdentifier] = oldClaims
        self.sendNewAvailableClaimsData(nac, frm, link)

    async def newAvailableClaimsPostClaimVerif(self, claimName):
        if claimName == "Job-Application":
            return await self.getNewAvailableClaimList("Job-Certificate")

    async def getNewAvailableClaimList(self, claimName):
        availClaims = []
        for sk in [sk for sk in self.getSchemaKeysToBeGenerated()
                   if sk.name == claimName]:
            schema = await self.issuer.wallet.getSchema(ID(sk))
            availClaims.append({
                NAME: schema.name,
                VERSION: schema.version,
                "schemaSeqNo": schema.seqId
            })
        return availClaims


def createAcme(name=None, wallet=None, basedirpath=None, port=None):
    return createAgent(AcmeAgent, name or "Acme Corp",
                       wallet or buildAcmeWallet(),
                       basedirpath, port, clientClass=TestClient)


if __name__ == "__main__":
    TestWalletedAgent.createAndRunAgent(
        AcmeAgent, "Acme Corp", wallet=buildAcmeWallet(), basedirpath=None,
        port=6666, looper=None, clientClass=TestClient)
