from plenum.common.log import getlogger
from plenum.common.types import f
from plenum.test.testable import Spyable

from sovrin_client.agent.agent import WalletedAgent
from sovrin_common.exceptions import LinkNotFound
from sovrin_common.txn import NONCE
from sovrin_client.test.agent.helper import getAgentCmdLineParams

logger = getlogger()


@Spyable(
    methods=[WalletedAgent._handlePing, WalletedAgent._handlePong])
class TestWalletedAgent(WalletedAgent):

    @staticmethod
    def getPassedArgs():
        return getAgentCmdLineParams()
