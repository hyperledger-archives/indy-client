from sovrin_client.test.agent.acme import createAcme
from sovrin_client.test.agent.helper import runAgentCli

runAgentCli(name='Acme',
            agentCreator=lambda: createAcme(port=6666))
