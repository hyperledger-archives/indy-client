from plenum.common.log import getlogger

from sovrin_client.agent.agent import createAgent
from sovrin_client.agent.constants import EVENT_NOTIFY_MSG
from sovrin_client.agent.exception import NonceNotFound
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

        portParam, = self.getPassedArgs()

        super().__init__('Thrift Bank', basedirpath, client, wallet,
                         port=portParam or port, loop=loop, config=config,
                         endpointArgs=self.getEndpointArgs(wallet))

        # maps invitation nonces to internal ids
        self._invites = {
            "77fbf9dc8c8e6acde33de98c6d747b28c": 1
        }

        self.availableClaims = []

        # mapping between requester identifier and corresponding available claims
        self.requesterAvailClaims = {}

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
    TestWalletedAgent.createAndRunAgent(
        ThriftAgent, "Thrift Bank", wallet=buildThriftWallet(), basedirpath=None,
        port=7777, looper=None, clientClass=TestClient)
