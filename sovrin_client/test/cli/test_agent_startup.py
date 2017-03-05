import pytest

from plenum.common.exceptions import BlowUp
from sovrin_client.test.agent.conftest import faberIsRunning as runningFaber


@pytest.fixture(scope="module")
def faberIsRunningWithoutNymAdded(emptyLooper, tdirWithPoolTxns, faberWallet,
                                  faberAgent):
    with pytest.raises(BlowUp):
        faber, faberWallet = runningFaber(emptyLooper, tdirWithPoolTxns,
                                          faberWallet, faberAgent, None)
        return faber, faberWallet


# def testAgentStartedWithoutPoolStarted(faberIsRunningWithoutNymAdded):
#     pass
#
#
# def testAgentStartedWithoutAdding(poolNodesStarted,
#                                   faberIsRunningWithoutNymAdded):
#         pass