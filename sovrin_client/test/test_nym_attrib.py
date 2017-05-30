import json
from contextlib import contextmanager

import base58
import libnacl.public
import pytest

from plenum.common.constants import ENC, REPLY, TXN_TIME, TXN_ID, \
    OP_FIELD_NAME, NYM, TARGET_NYM, \
    TXN_TYPE, ROLE, NONCE
from plenum.common.signer_simple import SimpleSigner
from plenum.common.types import f
from plenum.common.util import adict
from plenum.test import waits
from sovrin_client.client.client import Client
from sovrin_client.client.wallet.attribute import Attribute, LedgerStore
from sovrin_client.client.wallet.wallet import Wallet
from sovrin_client.test.helper import checkNacks, submitAndCheckRejects, \
    genTestClient, createNym, checkRejects
from sovrin_common.constants import SKEY
from sovrin_common.identity import Identity
from sovrin_common.txn_util import ATTRIB, TRUST_ANCHOR
from sovrin_common.util import getSymmetricallyEncryptedVal
from sovrin_node.test.helper import submitAndCheck, \
    makeAttribRequest, makeGetNymRequest, addAttributeAndCheck, TestNode, \
    getAttribute
from stp_core.common.log import getlogger
from stp_core.loop.eventually import eventually

logger = getlogger()

whitelistArray = []


def whitelist():
    return whitelistArray


@pytest.fixture(scope="module")
def attributeName():
    return 'name'


@pytest.fixture(scope="module")
def attributeValue():
    return 'Mario'


@pytest.fixture(scope="module")
def attributeData(attributeName, attributeValue):
    return json.dumps({attributeName: attributeValue})


@pytest.fixture(scope="module")
def addedRawAttribute(userWalletA: Wallet, trustAnchor: Client,
                      trustAnchorWallet: Wallet, attributeData, looper):
    attrib = Attribute(name='test attribute',
                       origin=trustAnchorWallet.defaultId,
                       value=attributeData,
                       dest=userWalletA.defaultId,
                       ledgerStore=LedgerStore.RAW)
    addAttributeAndCheck(looper, trustAnchor, trustAnchorWallet, attrib)
    return attrib


@pytest.fixture(scope="module")
def symEncData(attributeData):
    encData, secretKey = getSymmetricallyEncryptedVal(attributeData)
    return adict(data=attributeData, encData=encData, secretKey=secretKey)


@pytest.fixture(scope="module")
def addedEncryptedAttribute(userIdA, trustAnchor, trustAnchorWallet, looper,
                            symEncData):
    op = {
        TARGET_NYM: userIdA,
        TXN_TYPE: ATTRIB,
        ENC: symEncData.encData
    }

    return submitAndCheck(looper, trustAnchor, trustAnchorWallet, op)[0]


@pytest.fixture(scope="module")
def nonTrustAnchor(looper, nodeSet, tdir):
    sseed = b'a secret trust anchor seed......'
    signer = SimpleSigner(seed=sseed)
    c, _ = genTestClient(nodeSet, tmpdir=tdir, usePoolLedger=True)
    w = Wallet(c.name)
    w.addIdentifier(signer=signer)
    c.registerObserver(w.handleIncomingReply)
    looper.add(c)
    looper.run(c.ensureConnectedToNodes())
    return c, w


@pytest.fixture(scope="module")
def anotherTrustAnchor(nodeSet, steward, stewardWallet, tdir, looper):
    sseed = b'1 secret trust anchor seed......'
    signer = SimpleSigner(seed=sseed)
    c, _ = genTestClient(nodeSet, tmpdir=tdir, usePoolLedger=True)
    w = Wallet(c.name)
    w.addIdentifier(signer=signer)
    c.registerObserver(w.handleIncomingReply)
    looper.add(c)
    looper.run(c.ensureConnectedToNodes())
    createNym(looper, signer.identifier, steward, stewardWallet,
              role=TRUST_ANCHOR, verkey=signer.verkey)
    return c, w


def testCreateStewardWallet(stewardWallet):
    pass


@contextmanager
def whitelistextras(*msg):
    global whitelistArray
    ins = {m: (m in whitelistArray) for m in msg}
    [whitelistArray.append(m) for m, _in in ins.items() if not _in]
    yield
    [whitelistArray.remove(m) for m, _in in ins.items() if not _in]


def testNonStewardCannotCreateATrustAnchor(nodeSet, client1, wallet1, looper):

    with whitelistextras("UnknownIdentifier"):
        seed = b'a secret trust anchor seed......'
        trustAnchorSigner = SimpleSigner(seed=seed)

        trustAnchorNym = trustAnchorSigner.identifier

        op = {
            TARGET_NYM: trustAnchorNym,
            TXN_TYPE: NYM,
            ROLE: TRUST_ANCHOR
        }

        submitAndCheckRejects(looper=looper, client=client1, wallet=wallet1, op=op,
                              identifier=wallet1.defaultId,
                              contains="UnknownIdentifier")


def testStewardCreatesATrustAnchor(steward, addedTrustAnchor):
    pass


@pytest.mark.skip(reason="SOV-560. Cannot create another sponsor with same nym")
def testStewardCreatesAnotherTrustAnchor(nodeSet, steward, stewardWallet, looper,
                                     trustAnchorWallet):
    createNym(looper, trustAnchorWallet.defaultId, steward, stewardWallet, TRUST_ANCHOR)
    return trustAnchorWallet


def testNonTrustAnchorCannotCreateAUser(nodeSet, looper, nonTrustAnchor):
    with whitelistextras("UnknownIdentifier"):
        client, wallet = nonTrustAnchor
        useed = b'this is a secret apricot seed...'
        userSigner = SimpleSigner(seed=useed)

        userNym = userSigner.identifier

        op = {
            TARGET_NYM: userNym,
            TXN_TYPE: NYM
        }

        submitAndCheckRejects(looper, client, wallet, op,
                              identifier=wallet.defaultId,
                              contains="UnknownIdentifier")


def testTrustAnchorCreatesAUser(steward, userWalletA):
    pass


@pytest.fixture(scope="module")
def nymsAddedInQuickSuccession(nodeSet, addedTrustAnchor, looper,
                               trustAnchor, trustAnchorWallet):
    usigner = SimpleSigner()
    nym = usigner.verkey
    idy = Identity(identifier=nym)
    trustAnchorWallet.addTrustAnchoredIdentity(idy)
    # Creating a NYM request with same nym again
    req = idy.ledgerRequest()
    trustAnchorWallet._pending.appendleft((req, idy.identifier))
    reqs = trustAnchorWallet.preparePending()
    trustAnchor.submitReqs(*reqs)

    def check():
        assert trustAnchorWallet._trustAnchored[nym].seqNo

    timeout = waits.expectedTransactionExecutionTime(len(nodeSet))
    looper.run(eventually(check, timeout=timeout))

    timeout = waits.expectedReqNAckQuorumTime()
    looper.run(eventually(checkNacks,
                          trustAnchor,
                          req.reqId,
                          "is already added",
                          retryWait=1, timeout=timeout))
    count = 0
    for node in nodeSet:
        txns = node.domainLedger.getAllTxn()
        for seq, txn in txns.items():
            if txn[TXN_TYPE] == NYM and txn[TARGET_NYM] == usigner.identifier:
                count += 1

    assert(count == len(nodeSet))


def testTrustAnchorAddsAttributeForUser(addedRawAttribute):
    pass


def testClientGetsResponseWithoutConsensusForUsedReqId(nodeSet, looper, steward,
                                                       addedTrustAnchor, trustAnchor,
                                                       userWalletA,
                                                       attributeName,
                                                       attributeData,
                                                       addedRawAttribute):
    lastReqId = None
    replies = {}
    for msg, sender in reversed(trustAnchor.inBox):
        if msg[OP_FIELD_NAME] == REPLY:
            if not lastReqId:
                lastReqId = msg[f.RESULT.nm][f.REQ_ID.nm]
            if msg.get(f.RESULT.nm, {}).get(f.REQ_ID.nm) == lastReqId:
                replies[sender] = msg
            if len(replies) == len(nodeSet):
                break

    trustAnchorWallet = addedTrustAnchor
    attrib = Attribute(name=attributeName,
                       origin=trustAnchorWallet.defaultId,
                       value=attributeData,
                       dest=userWalletA.defaultId,
                       ledgerStore=LedgerStore.RAW)
    trustAnchorWallet.addAttribute(attrib)
    req = trustAnchorWallet.preparePending()[0]
    _, key = trustAnchorWallet._prepared.pop((req.identifier, req.reqId))
    req.reqId = lastReqId

    req.signature = trustAnchorWallet.signMsg(msg=req.signingState,
                                              identifier=req.identifier)
    trustAnchorWallet._prepared[req.identifier, req.reqId] = req, key
    trustAnchor.submitReqs(req)

    def chk():
        nonlocal trustAnchor, lastReqId, replies
        for node in nodeSet:
            last = node.spylog.getLast(TestNode.getReplyFromLedger.__name__)
            assert last
            result = last.result
            assert result is not None

            # TODO: Time is not equal as some precision is lost while storing
            # in oientdb, using seconds may be an option, need to think of a
            # use cases where time in milliseconds is required
            replies[node.clientstack.name][f.RESULT.nm].pop(TXN_TIME, None)
            result.result.pop(TXN_TIME, None)

            assert replies[node.clientstack.name][f.RESULT.nm] == {k:v for k, v in result.result.items() if v is not None}

    timeout = waits.expectedTransactionExecutionTime(len(nodeSet))
    looper.run(eventually(chk, retryWait=1, timeout=timeout))


@pytest.fixture(scope="module")
def checkAddAttribute(userWalletA, trustAnchor, trustAnchorWallet, attributeName,
                      attributeValue, addedRawAttribute, looper):
    getAttribute(looper=looper,
                 trustAnchor=trustAnchor,
                 trustAnchorWallet=trustAnchorWallet,
                 userIdA=userWalletA.defaultId,
                 attributeName=attributeName,
                 attributeValue=attributeValue)


def testTrustAnchorGetAttrsForUser(checkAddAttribute):
    pass


def testNonTrustAnchorCannotAddAttributeForUser(nodeSet, nonTrustAnchor, userIdA,
                                            looper, attributeData):
    with whitelistextras('UnauthorizedClientRequest'):
        client, wallet = nonTrustAnchor
        attrib = Attribute(name='test1 attribute',
                           origin=wallet.defaultId,
                           value=attributeData,
                           dest=userIdA,
                           ledgerStore=LedgerStore.RAW)
        reqs = makeAttribRequest(client, wallet, attrib)
        timeout = waits.expectedTransactionExecutionTime(len(nodeSet))
        looper.run(eventually(checkRejects,
                              client,
                              reqs[0].reqId,
                              "UnauthorizedClientRequest('Only identity owner/guardian can add attribute for that identity'",
                              retryWait=1, timeout=timeout))


def testOnlyUsersTrustAnchorCanAddAttribute(nodeSet, looper,
                                        steward, stewardWallet,
                                        attributeData, anotherTrustAnchor, userIdA):
    with whitelistextras("UnauthorizedClientRequest"):
        client, wallet = anotherTrustAnchor
        attrib = Attribute(name='test2 attribute',
                           origin=wallet.defaultId,
                           value=attributeData,
                           dest=userIdA,
                           ledgerStore=LedgerStore.RAW)
        reqs = makeAttribRequest(client, wallet, attrib)
        timeout = waits.expectedReqNAckQuorumTime()
        looper.run(eventually(checkRejects,
                              client,
                              reqs[0].reqId,
                              "UnauthorizedClientRequest('Only identity owner/guardian can add attribute for that identity'",
                              retryWait=1, timeout=timeout))


def testStewardCannotAddUsersAttribute(nodeSet, looper, steward,
                                       stewardWallet, userIdA, attributeData):
    with whitelistextras("UnauthorizedClientRequest"):
        attrib = Attribute(name='test3 attribute',
                           origin=stewardWallet.defaultId,
                           value=attributeData,
                           dest=userIdA,
                           ledgerStore=LedgerStore.RAW)
        reqs = makeAttribRequest(steward, stewardWallet, attrib)
        timeout = waits.expectedReqNAckQuorumTime()
        looper.run(eventually(checkRejects,
                              steward,
                              reqs[0].reqId,
                              "UnauthorizedClientRequest('Only identity owner/guardian can add attribute for that identity'",
                              retryWait=1, timeout=timeout))


@pytest.mark.skip(reason="SOV-560. Attribute encryption is done in client")
def testTrustAnchorAddedAttributeIsEncrypted(addedEncryptedAttribute):
    pass


@pytest.mark.skip(reason="SOV-560. Attribute Disclosure is not done for now")
def testTrustAnchorDisclosesEncryptedAttribute(addedEncryptedAttribute, symEncData,
                                           looper, userSignerA, trustAnchorSigner,
                                           trustAnchor):
    box = libnacl.public.Box(trustAnchorSigner.naclSigner.keyraw,
                             userSignerA.naclSigner.verraw)

    data = json.dumps({SKEY: symEncData.secretKey,
                       TXN_ID: addedEncryptedAttribute[TXN_ID]})
    nonce, boxedMsg = box.encrypt(data.encode(), pack_nonce=False)

    op = {
        TARGET_NYM: userSignerA.verstr,
        TXN_TYPE: ATTRIB,
        NONCE: base58.b58encode(nonce),
        ENC: base58.b58encode(boxedMsg)
    }
    submitAndCheck(looper, trustAnchor, op,
                   identifier=trustAnchorSigner.verstr)


@pytest.mark.skip(reason="SOV-561. Pending implementation")
def testTrustAnchorAddedAttributeCanBeChanged(addedRawAttribute):
    # TODO but only by user(if user has taken control of his identity) and
    # trustAnchor
    raise NotImplementedError


def testGetAttribute(nodeSet, addedTrustAnchor, trustAnchorWallet: Wallet, trustAnchor,
                     userIdA, addedRawAttribute, attributeData):
    assert attributeData in [a.value for a in trustAnchorWallet.getAttributesForNym(userIdA)]


# TODO: Ask Jason, if getting the latest attribute makes sense since in case
# of encrypted and hashed attributes, there is no name.
def testLatestAttrIsReceived(nodeSet, addedTrustAnchor, trustAnchorWallet, looper,
                             trustAnchor, userIdA):

    attr1 = json.dumps({'name': 'Mario'})
    attrib = Attribute(name='name',
                       origin=trustAnchorWallet.defaultId,
                       value=attr1,
                       dest=userIdA,
                       ledgerStore=LedgerStore.RAW)
    addAttributeAndCheck(looper, trustAnchor, trustAnchorWallet, attrib)
    assert attr1 in [a.value for a in trustAnchorWallet.getAttributesForNym(userIdA)]

    attr2 = json.dumps({'name': 'Luigi'})
    attrib = Attribute(name='name',
                       origin=trustAnchorWallet.defaultId,
                       value=attr2,
                       dest=userIdA,
                       ledgerStore=LedgerStore.RAW)
    addAttributeAndCheck(looper, trustAnchor, trustAnchorWallet, attrib)
    logger.debug([a.value for a in trustAnchorWallet.getAttributesForNym(userIdA)])
    assert attr2 in [a.value for a in
                     trustAnchorWallet.getAttributesForNym(userIdA)]


@pytest.mark.skip(reason="SOV-561. Test not implemented")
def testGetTxnsNoSeqNo():
    """
    Test GET_TXNS from client and do not provide any seqNo to fetch from
    """
    raise NotImplementedError


@pytest.mark.skip(reason="SOV-560. Come back to it later since "
                         "requestPendingTxns move to wallet")
def testGetTxnsSeqNo(nodeSet, addedTrustAnchor, tdir, trustAnchorWallet, looper):
    """
    Test GET_TXNS from client and provide seqNo to fetch from
    """
    trustAnchor = genTestClient(nodeSet, tmpdir=tdir, usePoolLedger=True)

    looper.add(trustAnchor)
    looper.run(trustAnchor.ensureConnectedToNodes())

    def chk():
        assert trustAnchor.spylog.count(trustAnchor.requestPendingTxns.__name__) > 0

    # TODO choose or create timeout in 'waits' on this case.
    looper.run(eventually(chk, retryWait=1, timeout=3))


def testNonTrustAnchoredNymCanDoGetNym(nodeSet, addedTrustAnchor,
                                   trustAnchorWallet, tdir, looper):
    signer = SimpleSigner()
    someClient, _ = genTestClient(nodeSet, tmpdir=tdir, usePoolLedger=True)
    wallet = Wallet(someClient.name)
    wallet.addIdentifier(signer=signer)
    someClient.registerObserver(wallet.handleIncomingReply)
    looper.add(someClient)
    looper.run(someClient.ensureConnectedToNodes())
    needle = trustAnchorWallet.defaultId
    makeGetNymRequest(someClient, wallet, needle)
    timeout = waits.expectedTransactionExecutionTime(len(nodeSet))
    looper.run(eventually(someClient.hasNym, needle, retryWait=1, timeout=timeout))


def testUserAddAttrsForHerSelf(nodeSet, looper, userClientA, userWalletA,
                               userIdA, attributeData):
    attr1 = json.dumps({'age': "25"})
    attrib = Attribute(name='test4 attribute',
                       origin=userIdA,
                       value=attr1,
                       dest=userIdA,
                       ledgerStore=LedgerStore.RAW)
    addAttributeAndCheck(looper, userClientA, userWalletA, attrib)


def testAttrWithNoDestAdded(nodeSet, looper, userClientA, userWalletA,
                               userIdA, attributeData):
    attr1 = json.dumps({'age': "24"})
    attrib = Attribute(name='test4 attribute',
                       origin=userIdA,
                       value=attr1,
                       dest=None,
                       ledgerStore=LedgerStore.RAW)
    addAttributeAndCheck(looper, userClientA, userWalletA, attrib)
