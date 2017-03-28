from sovrin_client.agent.constants import EVENT_NOTIFY_MSG
from plenum.common.log import getlogger
from sovrin_client.agent.runnable_agent import RunnableAgent
from sovrin_client.agent.agent import create_client

from sovrin_client.agent.agent import WalletedAgent
from sovrin_client.test.agent.helper import buildThriftWallet
from sovrin_client.test.helper import TestClient

logger = getlogger()


class ThriftAgent(WalletedAgent):

    async def postClaimVerif(self, claimName, link, frm):
        if claimName == "Loan-Application-Basic":
            self.notifyToRemoteCaller(EVENT_NOTIFY_MSG,
                                      "    Loan eligibility criteria satisfied,"
                                      " please send another claim "
                                      "'Loan-Application-KYC'\n",
                                      self.wallet.defaultId, frm)


def create_thrift(name=None, wallet=None, base_dir_path=None, port=7777, client=None):

    if client is None:
        client = create_client(base_dir_path=None, client_class=TestClient)

    agent = ThriftAgent(name=name or 'Thrift Bank',
                       basedirpath=base_dir_path,
                       client=client,
                       wallet=wallet or buildThriftWallet(),
                       port=port)

    agent._invites = {
        "77fbf9dc8c8e6acde33de98c6d747b28c": 1,
        "ousezru20ic4yz3j074trcgthwlsnfsef": 2
    }

    return agent

async def bootstrap_thrift(agent):
    pass

if __name__ == "__main__":
    args = RunnableAgent.parser_cmd_args()
    port = args[0]
    if port is None:
        port = 7777
    agent = create_thrift(name='Thrift Bank', wallet=buildThriftWallet(),
                          base_dir_path=None, port=port)
    RunnableAgent.run_agent(agent, bootstrap=bootstrap_thrift(agent))

