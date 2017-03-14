import pytest

from plenum.common.exceptions import PortNotAvailable, OperationError, \
    NoConsensusYet
from plenum.common.port_dispenser import genHa
from plenum.common.types import HA
from plenum.common.util import randomString, checkPortAvailable
from plenum.test.conftest import tdirWithPoolTxns
from sovrin_client.test.agent.conftest import emptyLooper, startAgent

from sovrin_client.test.agent.acme import createAcme as createAgent
from sovrin_client.test.agent.helper import buildAcmeWallet as agentWallet
from sovrin_client.test.cli.conftest \
    import acmeAddedByPhil as agentAddedBySponsor


agentPort = genHa()[1]


def getNewAgent(name, basedir, port, wallet):
    return createAgent(name, wallet, basedirpath=basedir, port=port)


def runAgent(looper, basedir, port, name=None, agent=None):
    wallet = agentWallet()
    name = name or "Agent"+ randomString(5)
    agent = agent or getNewAgent(name, basedir, port, wallet)
    agent._name = name
    return startAgent(looper, agent, wallet)


@pytest.fixture(scope="module")
def agentStarted(emptyLooper, tdirWithPoolTxns):
    runAgent(emptyLooper, tdirWithPoolTxns, agentPort, "Agent0")


def testCreateAgentDoesNotAllocatePort(tdirWithPoolTxns):
    for i in range(2):
        checkPortAvailable(HA("0.0.0.0", agentPort))
        getNewAgent("Agent0", tdirWithPoolTxns, agentPort, agentWallet())
        checkPortAvailable(HA("0.0.0.0", agentPort))


def testAgentStartedWithoutPoolStarted(emptyLooper, tdirWithPoolTxns):
    newAgentName = "Agent2"
    with pytest.raises(NoConsensusYet):
        runAgent(emptyLooper, tdirWithPoolTxns, agentPort,
                 name=newAgentName)
    emptyLooper.removeProdable(name=newAgentName)


def testStartAgentWithoutAddedToSovrin(poolNodesStarted, emptyLooper,
                                 tdirWithPoolTxns):
    newAgentName = "Agent3"
    with pytest.raises(OperationError) as oeinfo:
        runAgent(emptyLooper, tdirWithPoolTxns, agentPort,
                 name=newAgentName)
    assert "error occurred during operation: client request invalid: " \
           "UnknownIdentifier('{}',)".format(agentWallet().defaultId) \
           in str(oeinfo)
    emptyLooper.removeProdable(name=newAgentName)


def testStartNewAgentOnUsedPort(poolNodesStarted, tdirWithPoolTxns,
                                emptyLooper, agentAddedBySponsor,
                                agentStarted):

    with pytest.raises(PortNotAvailable):
        runAgent(emptyLooper, tdirWithPoolTxns, agentPort, name="Agent4")


def testStartAgentChecksForPortAvailability(poolNodesStarted, tdirWithPoolTxns,
                                            emptyLooper, agentAddedBySponsor):
    newAgentName1 = "Agent11"
    newAgentName2 = "Agent12"
    with pytest.raises(PortNotAvailable):
        agent = getNewAgent(newAgentName1, tdirWithPoolTxns, agentPort,
                            agentWallet())
        runAgent(emptyLooper, tdirWithPoolTxns, agentPort,
                 name=newAgentName2)
        runAgent(emptyLooper, tdirWithPoolTxns, agentPort,
                 name=newAgentName1, agent=agent)
    emptyLooper.removeProdable(name=newAgentName2)
