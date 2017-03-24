from sovrin_client.test.agent.faber import create_faber, bootstrap_faber
from sovrin_client.test.agent.helper import runAgentCli

# TODO: There is an issue, that if the agent's name has been already used in
# raet keep directory, and it's port is different than what is given below then,
# it will fail. Need to think about this problem in little detail and fix it.
runAgentCli(name='FaberCollege',
            agentCreator=lambda: create_faber(port=5555), bootstrap=bootstrap_faber)
