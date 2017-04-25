from sovrin_client.test.constants import primes
import warnings
from copy import deepcopy

from sovrin_common import strict_types

# typecheck during tests
strict_types.defaultShouldCheck = True

import pytest

from plenum.common.signer_simple import SimpleSigner
from plenum.common.constants import VERKEY, ALIAS, STEWARD, TXN_ID, TRUSTEE, TYPE

from sovrin_client.client.wallet.wallet import Wallet
from sovrin_common.constants import NYM, TRUST_ANCHOR
from sovrin_common.constants import TXN_TYPE, TARGET_NYM, ROLE
from sovrin_client.test.cli.helper import newCLI, addTrusteeTxnsToGenesis, addTxnToFile
from sovrin_node.test.helper import makePendingTxnsRequest, buildStewardClient, \
    TestNode
from sovrin_client.test.helper import addRole, \
    genTestClient, TestClient, createNym

# noinspection PyUnresolvedReferences
from plenum.test.conftest import tdir, nodeReg, up, ready, \
    whitelist, concerningLogLevels, logcapture, keySharedNodes, \
    startedNodes, tdirWithDomainTxns, txnPoolNodeSet, poolTxnData, dirName, \
    poolTxnNodeNames, allPluginsPath, tdirWithNodeKeepInited, tdirWithPoolTxns, \
    poolTxnStewardData, poolTxnStewardNames, getValueFromModule, \
    txnPoolNodesLooper, nodeAndClientInfoFilePath, patchPluginManager, \
    warncheck, warnfilters as plenum_warnfilters, setResourceLimits

# noinspection PyUnresolvedReferences
from sovrin_common.test.conftest import conf, tconf, poolTxnTrusteeNames, \
    domainTxnOrderedFields, looper


@pytest.fixture(scope="session")
def warnfilters(plenum_warnfilters):
    def _():
        plenum_warnfilters()
        warnings.filterwarnings('ignore', category=ResourceWarning, message='unclosed file')
    return _


@pytest.fixture(scope="module")
def primes1():
    P_PRIME1, Q_PRIME1 = primes.get("prime1")
    return dict(p_prime=P_PRIME1, q_prime=Q_PRIME1)


@pytest.fixture(scope="module")
def primes2():
    P_PRIME2, Q_PRIME2 = primes.get("prime2")
    return dict(p_prime=P_PRIME2, q_prime=Q_PRIME2)


@pytest.fixture(scope="module")
def updatedPoolTxnData(poolTxnData):
    data = deepcopy(poolTxnData)
    trusteeSeed = 'thisistrusteeseednotsteward12345'
    signer = SimpleSigner(seed=trusteeSeed.encode())
    t = {
        TARGET_NYM: signer.verkey,
        ROLE: TRUSTEE,
        TYPE: NYM,
        ALIAS: "Trustee1",
        TXN_ID: "6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4a"
    }
    data["seeds"]["Trustee1"] = trusteeSeed
    data["txns"].insert(0, t)
    return data


@pytest.fixture(scope="module")
def trusteeData(poolTxnTrusteeNames, updatedPoolTxnData):
    ret = []
    for name in poolTxnTrusteeNames:
        seed = updatedPoolTxnData["seeds"][name]
        txn = next((txn for txn in updatedPoolTxnData["txns"] if txn[ALIAS] == name), None)
        ret.append((name, seed.encode(), txn))
    return ret


@pytest.fixture(scope="module")
def trusteeWallet(trusteeData):
    name, sigseed, txn = trusteeData[0]
    wallet = Wallet('trustee')
    signer = SimpleSigner(seed=sigseed)
    wallet.addIdentifier(signer=signer)
    return wallet


# TODO: This fixture is present in sovrin_node too, it should be
# sovrin_common's conftest.
@pytest.fixture(scope="module")
#TODO devin
def trustee(nodeSet, looper, tdir, up, trusteeWallet):
    return buildStewardClient(looper, tdir, trusteeWallet)


@pytest.fixture(scope="module")
def stewardWallet(poolTxnStewardData):
    name, sigseed = poolTxnStewardData
    wallet = Wallet('steward')
    signer = SimpleSigner(seed=sigseed)
    wallet.addIdentifier(signer=signer)
    return wallet


@pytest.fixture(scope="module")
def steward(nodeSet, looper, tdir, stewardWallet):
    return buildStewardClient(looper, tdir, stewardWallet)


@pytest.fixture(scope="module")
def genesisTxns(stewardWallet: Wallet, trusteeWallet: Wallet):
    nym = stewardWallet.defaultId
    return [
        {
            TXN_TYPE: NYM,
            TARGET_NYM: nym,
            TXN_ID: "9c86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b",
            ROLE: STEWARD,
            VERKEY: stewardWallet.getVerkey()
        },
    ]


@pytest.fixture(scope="module")
def testNodeClass():
    return TestNode


@pytest.fixture(scope="module")
def testClientClass():
    return TestClient


@pytest.fixture(scope="module")
def tdirWithDomainTxnsUpdated(tdirWithDomainTxns, poolTxnTrusteeNames, trusteeData, tconf):
    addTrusteeTxnsToGenesis(poolTxnTrusteeNames, trusteeData, tdirWithDomainTxns, tconf.domainTransactionsFile)
    return tdirWithDomainTxns


@pytest.fixture(scope="module")
def updatedDomainTxnFile(tdir, tdirWithDomainTxnsUpdated, genesisTxns,
                         domainTxnOrderedFields, tconf):
    addTxnToFile(tdir, tconf.domainTransactionsFile, genesisTxns, domainTxnOrderedFields)


@pytest.fixture(scope="module")
def nodeSet(tconf, updatedPoolTxnData, updatedDomainTxnFile, txnPoolNodeSet):
    return txnPoolNodeSet


@pytest.fixture(scope="module")
def client1Signer():
    seed = b'client1Signer secret key........'
    signer = SimpleSigner(seed=seed)
    assert signer.verkey == '6JvpZp2haQgisbXEXE9NE6n3Tuv77MZb5HdF9jS5qY8m'
    return signer


@pytest.fixture("module")
def trustAnchorCli(looper, tdir):
    return newCLI(looper, tdir)


@pytest.fixture(scope="module")
def clientAndWallet1(client1Signer, looper, nodeSet, tdir, up):
    client, wallet = genTestClient(nodeSet, tmpdir=tdir, usePoolLedger=True)
    wallet = Wallet(client.name)
    wallet.addIdentifier(signer=client1Signer)
    return client, wallet


@pytest.fixture(scope="module")
def client1(clientAndWallet1, looper):
    client, wallet = clientAndWallet1
    looper.add(client)
    looper.run(client.ensureConnectedToNodes())
    return client


@pytest.fixture(scope="module")
def wallet1(clientAndWallet1):
    return clientAndWallet1[1]


@pytest.fixture(scope="module")
def trustAnchorWallet():
    wallet = Wallet('trustAnchor')
    seed = b'trust anchors are people too....'
    wallet.addIdentifier(seed=seed)
    return wallet


@pytest.fixture(scope="module")
def trustAnchor(nodeSet, addedTrustAnchor, trustAnchorWallet, looper, tdir):
    s, _ = genTestClient(nodeSet, tmpdir=tdir, usePoolLedger=True)
    s.registerObserver(trustAnchorWallet.handleIncomingReply)
    looper.add(s)
    looper.run(s.ensureConnectedToNodes())
    makePendingTxnsRequest(s, trustAnchorWallet)
    return s


@pytest.fixture(scope="module")
def addedTrustAnchor(nodeSet, steward, stewardWallet, looper,
                 trustAnchorWallet):
    createNym(looper,
              trustAnchorWallet.defaultId,
              steward,
              stewardWallet,
              role=TRUST_ANCHOR,
              verkey=trustAnchorWallet.getVerkey())
    return trustAnchorWallet


@pytest.fixture(scope="module")
def userWalletA(nodeSet, addedTrustAnchor, trustAnchorWallet, looper, trustAnchor):
    return addRole(looper, trustAnchor, trustAnchorWallet, 'userA', useDid=False,
                   addVerkey=False)


@pytest.fixture(scope="module")
def userWalletB(nodeSet, addedTrustAnchor, trustAnchorWallet, looper, trustAnchor):
    return addRole(looper, trustAnchor, trustAnchorWallet, 'userB', useDid=False,
                   addVerkey=False)


@pytest.fixture(scope="module")
def userIdA(userWalletA):
    return userWalletA.defaultId


@pytest.fixture(scope="module")
def userIdB(userWalletB):
    return userWalletB.defaultId


@pytest.fixture(scope="module")
def userClientA(nodeSet, userWalletA, looper, tdir):
    u, _ = genTestClient(nodeSet, tmpdir=tdir, usePoolLedger=True)
    u.registerObserver(userWalletA.handleIncomingReply)
    looper.add(u)
    looper.run(u.ensureConnectedToNodes())
    makePendingTxnsRequest(u, userWalletA)
    return u


@pytest.fixture(scope="module")
def userClientB(nodeSet, userWalletB, looper, tdir):
    u, _ = genTestClient(nodeSet, tmpdir=tdir, usePoolLedger=True)
    u.registerObserver(userWalletB.handleIncomingReply)
    looper.add(u)
    looper.run(u.ensureConnectedToNodes())
    makePendingTxnsRequest(u, userWalletB)
    return u
