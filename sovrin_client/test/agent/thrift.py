import os

from plenum.common.log import getlogger

from sovrin_client.agent.agent import createAgent, WalletedAgent
from sovrin_client.agent.runnable_agent import RunnableAgent
from sovrin_client.agent.constants import EVENT_NOTIFY_MSG
from sovrin_client.client.client import Client
from sovrin_client.client.wallet.wallet import Wallet
from sovrin_common.config_util import getConfig
from sovrin_client.test.agent.helper import buildThriftWallet
from sovrin_client.test.helper import TestClient

logger = getlogger()


class ThriftAgent(WalletedAgent, RunnableAgent):
    def __init__(self,
                 basedirpath: str,
                 client: Client = None,
                 wallet: Wallet = None,
                 port: int = None,
                 loop=None):
        if not basedirpath:
            config = getConfig()
            basedirpath = basedirpath or os.path.expanduser(config.baseDir)

        portParam, = self.get_passed_args()

        super().__init__('Thrift Bank', basedirpath, client, wallet,
                         portParam or port, loop=loop)

        # maps invitation nonces to internal ids
        self._invites = {
            "77fbf9dc8c8e6acde33de98c6d747b28c": 1
        }

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
    RunnableAgent.run_agent(
        ThriftAgent, "Thrift Bank", wallet=buildThriftWallet(), base_dir_path=None,
        port=7777, looper=None, client_class=TestClient)
