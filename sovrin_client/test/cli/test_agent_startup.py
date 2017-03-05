import pytest

from sovrin_client.agent.exception import AgentBootstrapFailed
from sovrin_client.test.agent.conftest import faberIsRunning as runningFaber


@pytest.fixture(scope="module")
def faberIsRunningWithoutNymAdded(emptyLooper, tdirWithPoolTxns, faberWallet,
                                  faberAgent):
    with pytest.raises(AgentBootstrapFailed):
        faber, faberWallet = runningFaber(emptyLooper, tdirWithPoolTxns,
                                          faberWallet, faberAgent, None)
        return faber, faberWallet


def testAgentStartedWithoutPoolStarted(faberIsRunningWithoutNymAdded):
    pass


def testAgentStartedWithoutAdding(poolNodesStarted,
                                  faberIsRunningWithoutNymAdded):
        pass