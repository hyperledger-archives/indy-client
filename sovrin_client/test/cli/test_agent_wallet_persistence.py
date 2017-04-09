import os
from typing import Dict

import pytest

from plenum.common.util import randomString, normalizedWalletFileName
from plenum.test.conftest import tdirWithPoolTxns
from sovrin_client.agent.agent import createAgent
from sovrin_client.test.agent.conftest import emptyLooper, startAgent

from sovrin_client.test.agent.acme import createAcme as createAcmeAgent, AcmeAgent
from sovrin_client.test.agent.helper import buildAcmeWallet as agentWallet
from sovrin_client.test.cli.conftest \
    import acmeAddedByPhil as agentAddedBySponsor
from sovrin_client.test.helper import TestClient
from stp_core.network.port_dispenser import genHa

agentPort = genHa()[1]


def getNewAgent(name, basedir, port, wallet):
    return createAcmeAgent(name, wallet, basedirpath=basedir, port=port)


def runAgent(looper, basedir, port, name=None, agent=None):
    wallet = agentWallet()
    wallet.name = name
    name = name or "Agent" + randomString(5)
    agent = agent or getNewAgent(name, basedir, port, wallet)
    return startAgent(looper, agent, wallet)


def _startAgent(looper, base_dir, port, name):
    agent, wallet = runAgent(looper, base_dir, port, name)
    return agent, wallet

@pytest.fixture(scope="module")
def agentStarted(emptyLooper, tdirWithPoolTxns):
    return _startAgent(emptyLooper, tdirWithPoolTxns, agentPort, "Agent0")


def changeAndPersistWallet(agent):
    walletName = normalizedWalletFileName(agent._wallet.name)
    expectedFilePath = os.path.join(agent.getContextDir(), walletName)
    assert "agents" in expectedFilePath
    assert agent.name.lower().replace(" ", "-") in expectedFilePath
    walletToBePersisted = agent._wallet
    walletToBePersisted.idsToSigners = {}
    agent.stop()
    assert os.path.isfile(expectedFilePath)
    return walletToBePersisted


def changePersistAndRestoreWallet(agent):
    assert agent
    changeAndPersistWallet(agent)
    agent.start(emptyLooper)
    assert agent._wallet.idsToSigners == {}


def testAgentPersistsWalletWhenStopped(poolNodesStarted, emptyLooper,
                                       agentAddedBySponsor, agentStarted):
    agent, _ = agentStarted
    changePersistAndRestoreWallet(agent)


def testAgentUsesRestoredWalletIfItHas(
        poolNodesStarted, emptyLooper, tdirWithPoolTxns,
        agentAddedBySponsor, agentStarted):
    agent, wallet = agentStarted
    changeAndPersistWallet(agent)

    newAgent = getNewAgent(agent.name, tdirWithPoolTxns, agentPort,
                        agentWallet())
    assert newAgent._wallet.idsToSigners == {}


def testAgentCreatesWalletIfItDoesntHaveOne(tdirWithPoolTxns):
    agent = createAgent(AcmeAgent, "Acme Corp",
                        wallet=None, basedirpath=tdirWithPoolTxns,
                        port=genHa()[1], clientClass=TestClient)
    assert agent._wallet is not None


def _compareWallets(unpersistedWallet, restoredWallet):
    def compare(old, new):
        if isinstance(old, Dict):
            for k, v in old.items():
                assert v == new.get(k)
        else:
            assert old == new

    compareList = [
        # from anoncreds wallet
        (unpersistedWallet.walletId, restoredWallet.walletId),
        (unpersistedWallet._repo.wallet.name, restoredWallet._repo.wallet.name),

        # from anoncreds wallet-in-memory
        (unpersistedWallet._schemasByKey, restoredWallet._schemasByKey),
        (unpersistedWallet._schemasById, restoredWallet._schemasById),
        (unpersistedWallet._pks, restoredWallet._pks),
        (unpersistedWallet._pkRs, restoredWallet._pkRs),
        (unpersistedWallet._accums, restoredWallet._accums),
        (unpersistedWallet._accumPks, restoredWallet._accumPks),
        # TODO: need to check for _tails, it is little bit different than
        # others (Dict instead of namedTuple or class)

        # from anoncreds issuer-wallet-in-memory
        (unpersistedWallet._sks, restoredWallet._sks),
        (unpersistedWallet._skRs, restoredWallet._skRs),
        (unpersistedWallet._accumSks, restoredWallet._accumSks),
        (unpersistedWallet._m2s, restoredWallet._m2s),
        (unpersistedWallet._attributes, restoredWallet._attributes),

    ]

    assert unpersistedWallet._repo.client is None
    assert restoredWallet._repo.client is not None
    for oldDict, newDict in compareList:
        compare(oldDict, newDict)


def testAgentWalletRestoration(poolNodesStarted, tdirWithPoolTxns, emptyLooper,
                  agentAddedBySponsor, agentStarted):
    agent, wallet = agentStarted
    unpersistedIssuerWallet = agent.issuer.wallet
    agent.stop()
    emptyLooper.removeProdable(agent)
    newAgent, newWallet = _startAgent(emptyLooper, tdirWithPoolTxns,
                                      agentPort, "Agent0")
    restoredIssuerWallet = newAgent.issuer.wallet
    _compareWallets(unpersistedIssuerWallet, restoredIssuerWallet)
