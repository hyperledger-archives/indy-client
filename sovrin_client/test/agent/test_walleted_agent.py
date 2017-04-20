from stp_core.common.log import getlogger
from plenum.common.util import getFormattedErrorMsg
from plenum.test.testable import spyable

from sovrin_client.agent.agent import WalletedAgent, createAgent, runAgent
from sovrin_client.client.client import Client
from sovrin_client.test.agent.helper import getAgentCmdLineParams, runAgentCli

logger = getlogger()


@spyable(
    methods=[WalletedAgent._handlePing, WalletedAgent._handlePong])
class TestWalletedAgent(WalletedAgent):

    @staticmethod
    def getPassedArgs():
        return getAgentCmdLineParams()

    @staticmethod
    def getEndpointArgs(wallet):
        endpointSeed = wallet._signerById(wallet.defaultId).seed if wallet \
            else None
        onlyListener = True
        return {'seed': endpointSeed,
                'onlyListener': onlyListener}

    @staticmethod
    def createAndRunAgent(name:str, agentClass=None, wallet=None, basedirpath=None,
                          port=None, looper=None, clientClass=Client,
                          bootstrap=True, cliAgentCreator=None):

        loop = looper.loop if looper else None
        _, with_cli = TestWalletedAgent.getPassedArgs()
        try:
            if cliAgentCreator and with_cli:
                runAgentCli(name=name, agentCreator=cliAgentCreator)
            else:
                assert agentClass
                agent = createAgent(agentClass, name, wallet, basedirpath,
                            port, loop, clientClass)
                runAgent(agent, looper, bootstrap)

        except Exception as exc:
            error = "Agent stopped: [cause : {}]".format(str(exc))
            logger.error(getFormattedErrorMsg(error))

