import pytest

from plenum.common.exceptions import ProdableAlreadyAdded, \
    PortNotAvailable
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
    # TODO: Somehow need to make sure we get agent with given name,
    # not default name
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
    # TODO: instead of SovrinNotAvailable, it should be something like
    # AgentNotAdded exception we should expect here. For that we'll have to
    # do changes in sovrin_public_repo.py (in _ensureReqCompleted,
    # to check for err and throw appropriate exception)
    with pytest.raises(SovrinNotAvailable):
        runAgent(emptyLooper, tdirWithPoolTxns, faberAgentPort, "Agent2")


def testStartSameAgentAgain(poolNodesStarted, tdirWithPoolTxns, emptyLooper,
                            faberAddedByPhil, faberAgentPort, agentStarted):
    with pytest.raises(ProdableAlreadyAdded):
        runAgent(emptyLooper, tdirWithPoolTxns, faberAgentPort, "Agent0")


def testStartNewAgentOnUsedPort(poolNodesStarted, tdirWithPoolTxns,
                                emptyLooper, faberAddedByPhil, faberAgentPort,
                                agentStarted):

    with pytest.raises(PortNotAvailable):
        runAgent(emptyLooper, tdirWithPoolTxns, faberAgentPort, "Agent3")
