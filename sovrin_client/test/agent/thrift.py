from anoncreds.protocol.types import AttribDef, AttribType
from plenum.common.log import getlogger

from sovrin_client.agent.agent import createAgent
from sovrin_client.agent.constants import EVENT_NOTIFY_MSG
from sovrin_client.client.client import Client
from sovrin_client.client.wallet.wallet import Wallet
from sovrin_client.test.agent.base_agent import BaseAgent
from sovrin_client.test.agent.helper import buildThriftWallet
from sovrin_client.test.agent.test_walleted_agent import TestWalletedAgent
from sovrin_client.test.helper import TestClient

logger = getlogger()


class ThriftAgent(BaseAgent):
    def __init__(self,
                 basedirpath: str,
                 client: Client = None,
                 wallet: Wallet = None,
                 port: int = None,
                 loop=None,
                 config=None):


        super().__init__('Thrift Bank', basedirpath, client, wallet,
                         port=port, loop=loop, config=config,
                         endpointArgs=self.getEndpointArgs(wallet))

        # maps invitation nonces to internal ids
        self._invites = {
            "77fbf9dc8c8e6acde33de98c6d747b28c": 1
        }

        self._attrDef = AttribDef('Thrift',
                                  [AttribType('title', encode=True),
                                   AttribType('first_name', encode=True),
                                   AttribType('last_name', encode=True),
                                   AttribType('address_1', encode=True),
                                   AttribType('address_2', encode=True),
                                   AttribType('address_3', encode=True),
                                   AttribType('postcode_zip', encode=True),
                                   AttribType('date_of_birth', encode=True)
                                   ])

        self._attrs = {
            1: self._attrDef.attribs(
                title='Mrs.',
                first_name='Alicia',
                last_name='Garcia',
                address_1='H-301',
                address_2='Street 1',
                address_3='UK',
                postcode_zip='G61 3NR',
                date_of_birth='December 28, 1990')
        }

    def getLinkNameByInternalId(self, internalId):
        return self._attrs[internalId]._vals["first_name"]

    async def postClaimVerif(self, claimName, link, frm):
        if claimName == "Loan-Application-Basic":
            self.notifyToRemoteCaller(EVENT_NOTIFY_MSG,
                                      "    Loan eligibility criteria satisfied,"
                                      " please send another claim "
                                      "'Loan-Application-KYC'\n",
                                      self.wallet.defaultId, frm)

    async def bootstrap(self):
        pass


def createThrift(name=None, wallet=None, basedirpath=None, port=None):
    return createAgent(ThriftAgent, name or "Thrift Bank",
                       wallet or buildThriftWallet(),
                       basedirpath, port, clientClass=TestClient)


if __name__ == "__main__":
    port = 7777
    TestWalletedAgent.createAndRunAgent(
        "Thrift Bank", agentClass=ThriftAgent, wallet=buildThriftWallet(),
        basedirpath=None, port=port, looper=None, clientClass=TestClient,
        cliAgentCreator=lambda: createThrift(port=port))
