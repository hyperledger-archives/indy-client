import pytest

from plenum.common.exceptions import BlowUp, ProdableAlreadyAdded, \
    PortNotAvailable
from plenum.common.looper import Looper
from plenum.test.conftest import tdirWithPoolTxns
from sovrin_client.test.agent.conftest import emptyLooper, faberAgent, startAgent
from sovrin_client.test.agent.faber import createFaber
from sovrin_client.test.agent.helper import buildFaberWallet


def getNewAgent(name, basedir, port, wallet):
    return createFaber(name, wallet,
                basedirpath=basedir,
                port=port)


def runAgent(looper, name, basedir, port):
    wallet = buildFaberWallet()
    agent = getNewAgent(name, basedir, port, wallet)
    return startAgent(looper, agent, wallet)

@pytest.fixture(scope="module")
def faberStarted(emptyLooper, tdirWithPoolTxns, faberAgentPort):
    runAgent(emptyLooper, "Agent", tdirWithPoolTxns, faberAgentPort)


@pytest.mark.asyncio
async def testAgentStartedWithoutPoolStarted(emptyLooper, tdirWithPoolTxns,
                                       faberAgentPort):
    with pytest.raises(BlowUp):
        runAgent(Looper(), "Agent", tdirWithPoolTxns, faberAgentPort)
    await emptyLooper.shutdown()


@pytest.mark.asyncio
async def testStartAgentWithoutAddedToSovrin(poolNodesStarted, emptyLooper,
                                 tdirWithPoolTxns, faberAgentPort):
    with pytest.raises(BlowUp):
        runAgent(Looper(), "Agent", tdirWithPoolTxns, faberAgentPort)
    await emptyLooper.shutdown()


@pytest.mark.asyncio
async def testStartSameAgentAgain(poolNodesStarted, tdirWithPoolTxns, emptyLooper,
                               faberAddedByPhil, faberAgentPort, faberStarted):
    with pytest.raises(ProdableAlreadyAdded):
        runAgent(Looper(), "Agent", tdirWithPoolTxns, faberAgentPort)
    await emptyLooper.shutdown()


@pytest.mark.asyncio
async def testStartNewAgentOnUsedPort(poolNodesStarted, tdirWithPoolTxns,
                                 emptyLooper, faberAddedByPhil, faberAgentPort,
                                 faberStarted):

    with pytest.raises(PortNotAvailable):
        runAgent(Looper(), "AgentNew", tdirWithPoolTxns, faberAgentPort)
    await emptyLooper.shutdown()

