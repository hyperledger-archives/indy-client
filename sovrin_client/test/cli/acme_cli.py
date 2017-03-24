from sovrin_client.test.agent.acme import create_acme, bootstrap_acme
from sovrin_client.test.agent.helper import runAgentCli

# TODO: There is an issue, that if the agent's name has been already used in
# raet keep directory, and it's port is different than what is given below then,
# it will fail. Need to think about this problem in little detail and fix it.
runAgentCli(name='Acme',
            agentCreator=lambda: create_acme(port=6666), bootstrap=bootstrap_acme)
