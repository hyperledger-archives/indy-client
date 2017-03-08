import pytest

from plenum.common.exceptions import BlowUp, ProdableAlreadyAdded, \
    PortNotAvailable
from plenum.common.looper import Looper
from plenum.common.util import checkPortAvailable
from plenum.test.conftest import tdirWithPoolTxns
from plenum.test.helper import waitUntillPortIsAvailable
from sovrin_client.test.agent.acme import createAcme
from sovrin_client.test.agent.conftest import faberIsRunning as runningFaber, \
    emptyLooper, faberWallet, acmeWallet, acmeIsRunning as runningAcme, \
    faberAgent, acmeAgent
from sovrin_client.test.agent.faber import createFaber
from sovrin_client.test.agent.helper import buildFaberWallet


def startFaberAgent(looper, tdirWithPoolTxns, faberWallet, faberAgent):
    return runningFaber(looper, tdirWithPoolTxns,
                                      faberWallet, faberAgent, None)


@pytest.fixture(scope="module")
def faberStarted(emptyLooper, tdirWithPoolTxns, faberWallet, faberAgent):
    startFaberAgent(emptyLooper, tdirWithPoolTxns, faberWallet, faberAgent)


def testAgentStartedWithoutPoolStarted(emptyLooper, tdirWithPoolTxns,
                                       faberWallet, faberAgent):
    with pytest.raises(BlowUp):
        startFaberAgent(Looper(), tdirWithPoolTxns,
                                             faberWallet, faberAgent)
    faberAgent.stop()


def testStartAgentWithoutAddedToSovrin(poolNodesStarted, emptyLooper,
                                 tdirWithPoolTxns, faberWallet, faberAgent):
    pass
    with pytest.raises(BlowUp):
        newWallet = buildFaberWallet()
        newFaberAgent = createFaber(faberWallet.name, newWallet,
                    basedirpath=tdirWithPoolTxns,
                    port=faberAgent.port)
        startFaberAgent(Looper(), tdirWithPoolTxns, newWallet, newFaberAgent)
    faberAgent.stop()


def testFaberRestartOnSamePort(poolNodesStarted, tdirWithPoolTxns, emptyLooper,
                               faberAddedByPhil, faberWallet,
                               faberAgent, faberStarted):
    with pytest.raises(ProdableAlreadyAdded):
        newWallet = buildFaberWallet()
        newFaberAgent = createFaber(faberWallet.name, newWallet,
                    basedirpath=tdirWithPoolTxns,
                    port=faberAgent.port)
        startFaberAgent(Looper(), tdirWithPoolTxns, newWallet, newFaberAgent)
    faberAgent.stop()


def testAcmeStartingOnFabersPort(poolNodesStarted, tdirWithPoolTxns,
                                 emptyLooper, faberAddedByPhil, faberAgent,
                                 acmeAddedByPhil, acmeWallet,
                                 faberStarted):
    acmeAgent = createAcme(acmeWallet.name, acmeWallet,
                            basedirpath=tdirWithPoolTxns,
                            port=faberAgent.port)

    with pytest.raises(PortNotAvailable):
        runningAcme(Looper(), tdirWithPoolTxns, acmeWallet,
                    acmeAgent, acmeAddedByPhil)

    waitUntillPortIsAvailable(emptyLooper, [faberAgent.port])
