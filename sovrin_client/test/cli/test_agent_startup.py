import pytest

from plenum.common.exceptions import ProdableAlreadyAdded, \
    PortNotAvailable, OperationError
from plenum.common.util import randomString
from plenum.test.conftest import tdirWithPoolTxns
from sovrin_client.test.agent.conftest import emptyLooper, startAgent
from sovrin_client.test.agent.faber import createFaber
from sovrin_client.test.agent.helper import buildFaberWallet
from sovrin_common.exceptions import SovrinNotAvailable


def getNewAgent(name, basedir, port, wallet):
    return createFaber(name, wallet,
                basedirpath=basedir,
                port=port)


def runAgent(looper, basedir, port, name=None):
    wallet = buildFaberWallet()
    name = name or "Agent"+ randomString(5)
    agent = getNewAgent(name, basedir, port, wallet)
    agent._name = name
    return startAgent(looper, agent, wallet)


@pytest.fixture(scope="module")
def agentStarted(emptyLooper, tdirWithPoolTxns, faberAgentPort):
    runAgent(emptyLooper, tdirWithPoolTxns, faberAgentPort, "Agent0")


def testAgentStartedWithoutPoolStarted(emptyLooper, tdirWithPoolTxns,
                                       faberAgentPort):
    with pytest.raises(SovrinNotAvailable):
        runAgent(emptyLooper, tdirWithPoolTxns, faberAgentPort, "Agent1")


def testStartAgentWithoutAddedToSovrin(poolNodesStarted, emptyLooper,
                                 tdirWithPoolTxns, faberAgentPort):
    with pytest.raises(OperationError) as oeinfo:
        runAgent(emptyLooper, tdirWithPoolTxns, faberAgentPort, "Agent2")
    faberWallet = buildFaberWallet()
    assert "error occurred during operation: client request invalid: " \
           "UnknownIdentifier('{}',)".format(faberWallet.defaultId) \
           in str(oeinfo)

def testStartSameAgentAgain(poolNodesStarted, tdirWithPoolTxns, emptyLooper,
                            faberAddedByPhil, faberAgentPort, agentStarted):
    with pytest.raises(ProdableAlreadyAdded):
        runAgent(emptyLooper, tdirWithPoolTxns, faberAgentPort, "Agent0")


def testStartNewAgentOnUsedPort(poolNodesStarted, tdirWithPoolTxns,
                                emptyLooper, faberAddedByPhil, faberAgentPort,
                                agentStarted):

    with pytest.raises(PortNotAvailable):
        runAgent(emptyLooper, tdirWithPoolTxns, faberAgentPort, "Agent3")
