import os

from plenum.common.txn import NAME, VERSION

from anoncreds.protocol.types import AttribType, AttribDef, ID, SchemaKey
from sovrin_client.agent.agent import createAgent, runAgent
from sovrin_client.agent.exception import NonceNotFound
from sovrin_client.client.client import Client
from sovrin_client.client.wallet.wallet import Wallet
from sovrin_client.test.agent.bulldog_helper import getBulldogLogger
from sovrin_common.config_util import getConfig
from sovrin_client.test.agent.helper import buildBulldogWallet
from sovrin_client.test.agent.test_walleted_agent import TestWalletedAgent
from sovrin_client.test.conftest import primes
from sovrin_client.test.helper import TestClient


class BulldogAgent(TestWalletedAgent):
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
        agentLogger = getBulldogLogger(basedirpath)

        super().__init__('Bulldog', basedirpath, client, wallet,
                         portParam or port, loop=loop,
                         agentLogger=agentLogger)

        self.availableClaims = []

        # maps invitation nonces to internal ids
        self._invites = {
            '2e9882ea71976ddf9': 1,
            "2d03828a7383ea3ad": 2
        }

        self._attrDef = AttribDef('bulldog',
                                  [AttribType('title', encode=True),
                                   AttribType('first_name', encode=True),
                                   AttribType('last_name', encode=True),
                                   AttribType('address_1', encode=True),
                                   AttribType('address_2', encode=True),
                                   AttribType('address_3', encode=True),
                                   AttribType('postcode_zip', encode=True),
                                   AttribType('date_of_birth', encode=True),
                                   AttribType('account_type', encode=True),
                                   AttribType('year_opened', encode=True),
                                   AttribType('account_status', encode=True)
                                   ])

        # maps internal ids to attributes
        self._attrs = {
            1: self._attrDef.attribs(
                title='Mrs.',
                first_name='Alicia',
                last_name='Garcia',
                address_1='H-301',
                address_2='Street 1',
                address_3='UK',
                postcode_zip='G61 3NR',
                date_of_birth='December 28, 1990',
                account_type='savings',
                year_opened='2000',
                account_status='active'),
            2: self._attrDef.attribs(
                title='Mrs.',
                first_name='Jay',
                last_name='Raj',
                address_1='222',
                address_2='Baker Street',
                address_3='UK',
                postcode_zip='G61 3NR',
                date_of_birth='January 15, 1980',
                account_type='savings',
                year_opened='1999',
                account_status='active')
        }

        claimVersionFileName = 'bulldog-schema-version.txt'
        claimVersionNumber = 0.8
        claimVersionFilePath = '{}/{}'.format(basedirpath, claimVersionFileName)
        # get version number from file
        if os.path.isfile(claimVersionFilePath):
            try:
                with open(claimVersionFilePath, mode='r+') as file:
                    claimVersionNumber = float(file.read()) + 0.1
                    file.seek(0)
                    # increment version and update file
                    file.write(str(claimVersionNumber))
                    file.truncate()
            except OSError as e:
                agentLogger.warn('Error occurred while reading version file:'
                                   'error:{}'.format(e))
                raise e
            except ValueError as e:
                agentLogger.warn('Invalid version number')
                raise e
        else:
            try:
                with open(claimVersionFilePath, mode='w') as file:
                    file.write(str(claimVersionNumber))
            except OSError as e:
                agentLogger.warn('Error creating version file {}'.format(e))
                raise e

        self._schemaKey = SchemaKey('Banking-Relationship',
                                               str(claimVersionNumber),
                                               self.wallet.defaultId)

    def getInternalIdByInvitedNonce(self, nonce):
        if nonce in self._invites:
            return self._invites[nonce]
        else:
            raise NonceNotFound

    def isClaimAvailable(self, link, claimName):
        return claimName == 'Banking-Relationship'

    def getAvailableClaimList(self):
        return self.availableClaims

    async def postClaimVerif(self, claimName, link, frm):
        pass

    async def initAvailableClaimList(self):
        schema = await self.issuer.wallet.getSchema(ID(self._schemaKey))
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
        schema = await self.issuer.genSchema(self._schemaKey.name,
                                                 self._schemaKey.version,
                                                 self._attrDef.attribNames(),
                                                 'CL')
        schemaId = ID(schemaKey=schema.getKey(), schemaId=schema.seqId)
        p_prime, q_prime = primes["prime2"]
        await self.issuer.genKeys(schemaId, p_prime=p_prime, q_prime=q_prime)
        await self.issuer.issueAccumulator(schemaId=schemaId, iA='110', L=5)
        await self.initAvailableClaimList()

    async def bootstrap(self):
        await self.addSchemasToWallet()


def createBulldog(name=None, wallet=None, basedirpath=None, port=None):
    return createAgent(BulldogAgent, name or "Bulldog",
                       wallet or buildBulldogWallet(),
                       basedirpath, port, clientClass=TestClient)


if __name__ == "__main__":
    bulldog = createBulldog(port=8787)
    runAgent(bulldog)
