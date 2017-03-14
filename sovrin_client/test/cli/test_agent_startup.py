import pytest

from plenum.common.exceptions import ProdableAlreadyAdded, \
    PortNotAvailable, OperationError, NoConsensusYet
from plenum.common.types import HA
from plenum.common.util import randomString, checkPortAvailable
from plenum.test.conftest import tdirWithPoolTxns
from sovrin_client.test.agent.conftest import emptyLooper, startAgent
from sovrin_client.test.agent.faber import createFaber
from sovrin_client.test.agent.helper import buildFaberWallet


def getNewAgent(name, basedir, port, wallet):
    return createFaber(name, wallet,
                basedirpath=basedir,
                port=port)


def runAgent(looper, basedir, port, name=None, agent=None):
    wallet = buildFaberWallet()
    name = name or "Agent"+ randomString(5)
    agent = agent or getNewAgent(name, basedir, port, wallet)
    agent._name = name
    return startAgent(looper, agent, wallet)


@pytest.fixture(scope="module")
def agentStarted(emptyLooper, tdirWithPoolTxns, faberAgentPort):
    runAgent(emptyLooper, tdirWithPoolTxns, faberAgentPort, "Agent0")


def testCreateAgentDoesNotAllocatePort(tdirWithPoolTxns, faberAgentPort):
    for i in range(2):
        checkPortAvailable(HA("0.0.0.0", faberAgentPort))
        getNewAgent("Agent0", tdirWithPoolTxns, faberAgentPort, buildFaberWallet())
        checkPortAvailable(HA("0.0.0.0", faberAgentPort))


def testStartAgentChecksForPortAvailability(poolNodesStarted, tdirWithPoolTxns,
                                emptyLooper, faberAddedByPhil, faberAgentPort):
    newAgentName1 = "Agent11"
    newAgentName2 = "Agent12"
    with pytest.raises(PortNotAvailable):
        agent1 = getNewAgent(newAgentName1, tdirWithPoolTxns, faberAgentPort,
                    buildFaberWallet())
        runAgent(emptyLooper, tdirWithPoolTxns, faberAgentPort,
                 name=newAgentName2)
        runAgent(emptyLooper, tdirWithPoolTxns, faberAgentPort,
                 name=newAgentName1, agent=agent1)
    emptyLooper.removeProdable(name=newAgentName1)
    emptyLooper.removeProdable(name=newAgentName2)


def testAgentStartedWithoutPoolStarted(emptyLooper, tdirWithPoolTxns,
                                       faberAgentPort):
    newAgentName = "Agent2"
    with pytest.raises(NoConsensusYet):
        runAgent(emptyLooper, tdirWithPoolTxns, faberAgentPort,
                 name=newAgentName)
    emptyLooper.removeProdable(name=newAgentName)


def testStartAgentWithoutAddedToSovrin(poolNodesStarted, emptyLooper,
                                 tdirWithPoolTxns, faberAgentPort):
    newAgentName = "Agent3"
    with pytest.raises(OperationError) as oeinfo:
        runAgent(emptyLooper, tdirWithPoolTxns, faberAgentPort,
                 name=newAgentName)
    faberWallet = buildFaberWallet()
    assert "error occurred during operation: client request invalid: " \
           "UnknownIdentifier('{}',)".format(faberWallet.defaultId) \
           in str(oeinfo)
    emptyLooper.removeProdable(name=newAgentName)


def testStartNewAgentOnUsedPort(poolNodesStarted, tdirWithPoolTxns,
                                emptyLooper, faberAddedByPhil, faberAgentPort,
                                agentStarted):

    with pytest.raises(PortNotAvailable):
        runAgent(emptyLooper, tdirWithPoolTxns, faberAgentPort, name="Agent4")
