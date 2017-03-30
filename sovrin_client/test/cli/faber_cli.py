from sovrin_client.test.agent.faber import createFaber
from sovrin_client.test.agent.helper import runAgentCli

runAgentCli(name='FaberCollege',
            agentCreator=lambda: createFaber(port=5555))
