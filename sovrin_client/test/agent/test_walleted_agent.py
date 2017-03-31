from plenum.common.log import getlogger
from plenum.common.types import f
from plenum.common.util import getFormattedErrorMsg
from plenum.test.testable import Spyable

from sovrin_client.agent.agent import WalletedAgent, createAgent, runAgent
from sovrin_client.client.client import Client
from sovrin_common.exceptions import LinkNotFound
from sovrin_common.constants import NONCE
from sovrin_client.test.agent.helper import getAgentCmdLineParams

logger = getlogger()


@Spyable(
    methods=[WalletedAgent._handlePing, WalletedAgent._handlePong])
class TestWalletedAgent(WalletedAgent):

    @staticmethod
    def getPassedArgs():
        return getAgentCmdLineParams()

    def createAndRunAgent(agentClass, name, wallet=None, basedirpath=None,
                      port=None, looper=None, clientClass=Client, bootstrap=True):
        try:
            loop = looper.loop if looper else None
            agent = createAgent(agentClass, name, wallet, basedirpath, port,
                                loop,
                                clientClass)
            runAgent(agent, looper, bootstrap)
            return agent
        except Exception as exc:
            error = "Agent startup failed: [cause : {}]".format(str(exc))
            logger.error(getFormattedErrorMsg(error))
