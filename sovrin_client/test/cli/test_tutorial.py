import json

import pytest
from plenum.common.eventually import eventually
from plenum.test.cli.helper import exitFromCli, \
    createAndAssertNewKeyringCreation
from sovrin_common.exceptions import InvalidLinkException
from sovrin_common.txn import ENDPOINT

from sovrin_client.client.wallet.link import Link, constant
from sovrin_client.test.cli.helper import getFileLines, prompt_is, doubleBraces


def getSampleLinkInvitation():
    return {
        "link-invitation": {
            "name": "Acme Corp",
            "identifier": "7YD5NKn3P4wVJLesAmA1rr7sLPqW9mR1nhFdKD518k21",
            "nonce": "57fbf9dc8c8e6acde33de98c6d747b28c",
            "endpoint": "127.0.0.1:1213"
        },
        "proof-requests": [{
            "name": "Job-Application",
            "version": "0.2",
            "attributes": {
                "first_name": "string",
                "last_name": "string",
                "phone_number": "string",
                "degree": "string",
                "status": "string",
                "ssn": "string"
            }
        }],
        "sig": "KDkI4XUePwEu1K01u0DpDsbeEfBnnBfwuw8e4DEPK+MdYXv"
               "VsXdSmBJ7yEfQBm8bSJuj6/4CRNI39fFul6DcDA=="
    }


@pytest.fixture(scope="module")
def philCli(be, do, philCLI):
    be(philCLI)
    do('prompt Phil', expect=prompt_is('Phil'))

    do('new keyring Phil', expect=['New keyring Phil created',
                                   'Active keyring set to "Phil"'])

    mapper = {
        'seed': '11111111111111111111111111111111',
        'idr': '5rArie7XKukPCaEwq5XGQJnM9Fc5aZE3M9HAPVfMU2xC'}
    do('new key with seed {seed}', expect=['Key created in keyring Phil',
                                           'Identifier for key is {idr}',
                                           'Current identifier set to {idr}'],
       mapper=mapper)

    return philCLI


@pytest.fixture(scope="module")
def faberAddedByPhil(be, do, poolNodesStarted, philCli, connectedToTest,
                     nymAddedOut, faberMap):
    be(philCli)
    if not philCli._isConnectedToAnyEnv():
        do('connect test', within=3,
           expect=connectedToTest)

    do('send NYM dest={target} role=SPONSOR',
       within=3,
       expect=nymAddedOut, mapper=faberMap)
    return philCli


@pytest.fixture(scope="module")
def acmeAddedByPhil(be, do, poolNodesStarted, philCli, connectedToTest,
                    nymAddedOut, acmeMap):
    be(philCli)
    if not philCli._isConnectedToAnyEnv():
        do('connect test', within=3,
           expect=connectedToTest)

    do('send NYM dest={target} role=SPONSOR',
       within=3,
       expect=nymAddedOut, mapper=acmeMap)
    return philCli


@pytest.fixture(scope="module")
def thriftAddedByPhil(be, do, poolNodesStarted, philCli, connectedToTest,
                      nymAddedOut, thriftMap):
    be(philCli)
    if not philCli._isConnectedToAnyEnv():
        do('connect test', within=3,
           expect=connectedToTest)

    do('send NYM dest={target} role=SPONSOR',
       within=3,
       expect=nymAddedOut, mapper=thriftMap)
    return philCli


def checkIfInvalidAttribIsRejected(do, map):
    data = json.loads(map.get('invalidEndpointAttr'))
    endpoint = data.get(ENDPOINT)
    errorMsg = 'client request invalid: InvalidClientRequest(' \
               '"invalid endpoint: \'{}\'",)'.format(endpoint)

    do("send ATTRIB dest={target} raw={invalidEndpointAttr}",
       within=5,
       expect=[errorMsg],
       mapper=map)


@pytest.fixture(scope="module")
def faberWithEndpointAdded(be, do, philCli, faberAddedByPhil,
                           faberMap, attrAddedOut):
    be(philCli)
    checkIfInvalidAttribIsRejected(do, faberMap)
    do('send ATTRIB dest={target} raw={endpointAttr}',
       within=5,
       expect=attrAddedOut,
       mapper=faberMap)
    return philCli


@pytest.fixture(scope="module")
def acmeWithEndpointAdded(be, do, philCli, acmeAddedByPhil,
                          acmeMap, attrAddedOut):
    be(philCli)
    checkIfInvalidAttribIsRejected(do, acmeMap)
    do('send ATTRIB dest={target} raw={endpointAttr}',
       within=3,
       expect=attrAddedOut,
       mapper=acmeMap)
    return philCli


@pytest.fixture(scope="module")
def thriftWithEndpointAdded(be, do, philCli, thriftAddedByPhil,
                            thriftMap, attrAddedOut):
    be(philCli)
    checkIfInvalidAttribIsRejected(do, thriftMap)
    do('send ATTRIB dest={target} raw={endpointAttr}',
       within=3,
       expect=attrAddedOut,
       mapper=thriftMap)
    return philCli


def connectIfNotAlreadyConnected(do, expectMsgs, userCli, userMap):
    # TODO: Shouldn't this be testing the cli command `status`?
    if not userCli._isConnectedToAnyEnv():
        do('connect test', within=3,
           expect=expectMsgs,
           mapper=userMap)


def getTotalLinks(userCli):
    return len(userCli.activeWallet._links)


def getTotalAvailableClaims(userCli):
    availableClaimsCount = 0
    for li in userCli.activeWallet._links.values():
        availableClaimsCount += len(li.availableClaims)
    return availableClaimsCount


def getTotalSchemas(userCli):
    async def getTotalSchemasCoro():
        return 0 if userCli.agent.prover is None \
            else len(await userCli.agent.prover.wallet.getAllSchemas())
    return userCli.looper.run(getTotalSchemasCoro)


def getTotalClaimsRcvd(userCli):
    async def getTotalClaimsRcvdCoro():
        return 0 if userCli.agent.prover is None \
            else len((await userCli.agent.prover.wallet.getAllClaims()).keys())
    return userCli.looper.run(getTotalClaimsRcvdCoro)


def setPromptAndKeyring(do, name, newKeyringOut, userMap):
    do('prompt {}'.format(name), expect=prompt_is(name))
    do('new keyring {}'.format(name), expect=newKeyringOut, mapper=userMap)


@pytest.fixture(scope="module")
def preRequisite(poolNodesStarted,
                 faberIsRunning, acmeIsRunning, thriftIsRunning,
                 faberWithEndpointAdded, acmeWithEndpointAdded,
                 thriftWithEndpointAdded):
    pass


@pytest.fixture(scope="module")
def walletCreatedForTestEnv(preRequisite, be, do, earlCLI, connectedToTest):
    be(earlCLI)
    createAndAssertNewKeyringCreation(do, "default1")
    createAndAssertNewKeyringCreation(do, "default2")
    connectIfNotAlreadyConnected(do, connectedToTest, earlCLI, {})
    createAndAssertNewKeyringCreation(do, "test2")
    exitFromCli(do)


@pytest.fixture(scope="module")
def aliceCli(preRequisite, be, do, walletCreatedForTestEnv,
             aliceCLI, newKeyringOut, aliceMap):
    be(aliceCLI)
    setPromptAndKeyring(do, "Alice", newKeyringOut, aliceMap)
    return aliceCLI


@pytest.fixture(scope="module")
def susanCli(preRequisite, be, do, susanCLI, newKeyringOut, susanMap):
    be(susanCLI)
    setPromptAndKeyring(do, "Susan", newKeyringOut, susanMap)
    return susanCLI


def testNotConnected(be, do, aliceCli, notConnectedStatus):
    be(aliceCli)
    do('status', expect=notConnectedStatus)


def testShowInviteNotExists(be, do, aliceCli, fileNotExists, faberMap):
    be(aliceCli)
    do('show {invite-not-exists}', expect=fileNotExists, mapper=faberMap)


def testShowInviteWithDirPath(be, do, aliceCli, fileNotExists, faberMap):
    be(aliceCli)
    do('show sample', expect=fileNotExists, mapper=faberMap)


def testLoadLinkInviteWithoutSig():
    li = getSampleLinkInvitation()
    del li["sig"]
    with pytest.raises(InvalidLinkException) as excinfo:
        Link.validate(li)
    assert "Field not found in given input: sig" in str(excinfo.value)


def testShowFaberInvite(be, do, aliceCli, faberMap):
    be(aliceCli)
    inviteContents = doubleBraces(getFileLines(faberMap.get("invite")))
    do('show {invite}', expect=inviteContents,
       mapper=faberMap)


def testLoadInviteNotExists(be, do, aliceCli, fileNotExists, faberMap):
    be(aliceCli)
    do('load {invite-not-exists}', expect=fileNotExists, mapper=faberMap)


@pytest.fixture(scope="module")
def faberInviteLoadedByAlice(be, do, aliceCli, loadInviteOut, faberMap):
    totalLinksBefore = getTotalLinks(aliceCli)
    be(aliceCli)
    do('load {invite}', expect=loadInviteOut, mapper=faberMap)
    assert totalLinksBefore + 1 == getTotalLinks(aliceCli)
    return aliceCli


def testLoadFaberInvite(faberInviteLoadedByAlice):
    pass


def testShowLinkNotExists(be, do, aliceCli, linkNotExists, faberMap):
    be(aliceCli)
    do('show link {inviter-not-exists}',
       expect=linkNotExists,
       mapper=faberMap)


def testShowFaberLink(be, do, aliceCli, faberInviteLoadedByAlice,
                      showUnSyncedLinkOut, faberMap):
    be(aliceCli)
    cp = faberMap.copy()
    cp.update(endpoint='<unknown, waiting for sync>',
              last_synced='<this link has not yet been synchronized>')
    do('show link {inviter}', expect=showUnSyncedLinkOut, mapper=cp)


def testSyncLinkNotExists(be, do, aliceCli, linkNotExists, faberMap):
    be(aliceCli)
    do('sync {inviter-not-exists}', expect=linkNotExists, mapper=faberMap)


def testSyncFaberWhenNotConnected(be, do, aliceCli, faberMap,
                                  faberInviteLoadedByAlice,
                                  syncWhenNotConnected):
    be(aliceCli)
    do('sync {inviter}', expect=syncWhenNotConnected,
       mapper=faberMap)


def testAcceptUnSyncedFaberInviteWhenNotConnected(be, do, aliceCli,
                                                  faberInviteLoadedByAlice,
                                                  acceptUnSyncedWhenNotConnected,
                                                  faberMap):
    be(aliceCli)
    do('accept invitation from {inviter}',
       expect=acceptUnSyncedWhenNotConnected,
       mapper=faberMap)


# def testAcceptUnSyncedFaberInvite(be, do, aliceCli, preRequisite,
#                                   faberInviteLoadedByAlice,
#                                   acceptUnSyncedWithoutEndpointWhenConnected,
#                                   faberMap, connectedToTest):
#     be(aliceCli)
#     connectIfNotAlreadyConnected(do, connectedToTest, aliceCli, faberMap)
#
#     checkWalletStates(aliceCli, totalLinks=1, totalAvailableClaims=0,
#                       totalSchemas=0, totalClaimsRcvd=0)
#     do('accept invitation from {inviter}',
#        within=13,
#        expect=acceptUnSyncedWithoutEndpointWhenConnected,
#        mapper=faberMap)
#     checkWalletStates(aliceCli, totalLinks=1, totalAvailableClaims=0,
#                       totalSchemas=0, totalClaimsRcvd=0)


@pytest.fixture(scope="module")
def faberInviteSyncedWithoutEndpoint(be, do, aliceCli, faberMap,
                                     preRequisite,
                                     faberInviteLoadedByAlice,
                                     connectedToTest,
                                     linkNotYetSynced,
                                     syncLinkOutWithoutEndpoint):
    be(aliceCli)
    connectIfNotAlreadyConnected(do, connectedToTest, aliceCli, faberMap)

    do('sync {inviter}', within=2,
       expect=syncLinkOutWithoutEndpoint,
       mapper=faberMap)
    return aliceCli


def testSyncFaberInviteWithoutEndpoint(faberInviteSyncedWithoutEndpoint):
    pass


def testShowSyncedFaberInvite(be, do, aliceCli, faberMap, linkNotYetSynced,
                              faberInviteSyncedWithoutEndpoint,
                              showSyncedLinkWithoutEndpointOut):

    be(aliceCli)

    cp = faberMap.copy()
    cp.update(endpoint='<unknown, waiting for sync>',
              last_synced='<this link has not yet been synchronized>')

    do('show link {inviter}', within=4,
       expect=showSyncedLinkWithoutEndpointOut,
       # TODO, need to come back to not_expect
       # not_expect=linkNotYetSynced,
       mapper=cp)


def syncInvite(be, do, userCli, expectedMsgs, mapping):
    be(userCli)

    do('sync {inviter}', within=2,
       expect=expectedMsgs,
       mapper=mapping)


@pytest.fixture(scope="module")
def faberInviteSyncedWithEndpoint(be, do, faberMap, aliceCLI, preRequisite,
                                  faberInviteSyncedWithoutEndpoint,
                                  syncLinkOutWithEndpoint):
    cp = faberMap.copy()
    cp.update(last_synced='<this link has not yet been synchronized>')
    syncInvite(be, do, aliceCLI, syncLinkOutWithEndpoint, cp)
    return aliceCLI


def testSyncFaberInvite(faberInviteSyncedWithEndpoint):
    pass


def testShowSyncedFaberInviteWithEndpoint(be, do, aliceCLI, faberMap,
                                          faberInviteSyncedWithEndpoint,
                                          showSyncedLinkWithEndpointOut):
    be(aliceCLI)
    cp = faberMap.copy()
    cp.update(last_synced='just now')
    do('show link {inviter}', expect=showSyncedLinkWithEndpointOut, mapper=cp)


def testPingBeforeAccept(be, do, aliceCli, faberMap, connectedToTest,
                         faberInviteSyncedWithEndpoint):
    be(aliceCli)
    connectIfNotAlreadyConnected(do, connectedToTest, aliceCli, faberMap)
    do('ping {inviter}',
       within=3,
       expect=[
           'Ping sent.',
           'Error processing ping. Link is not yet created.'
       ],
       mapper=faberMap)


def testAcceptNotExistsLink(be, do, aliceCli, linkNotExists, faberMap):
    be(aliceCli)
    do('accept invitation from {inviter-not-exists}',
       expect=linkNotExists, mapper=faberMap)


def getSignedRespMsg(msg, signer):
    signature = signer.sign(msg)
    msg["signature"] = signature
    return msg


def acceptInvitation(be, do, userCli, agentMap, expect):
    be(userCli)
    do("accept invitation from {inviter}",
       within=15,
       mapper=agentMap,
       expect=expect,
       not_expect=[
           "Observer threw an exception",
           "Identifier is not yet written to Sovrin"]
       )


@pytest.fixture(scope="module")
def aliceAcceptedFaberInvitation(be, do, aliceCli, faberMap,
                                 preRequisite,
                                 syncedInviteAcceptedWithClaimsOut,
                                 faberInviteSyncedWithEndpoint):
    acceptInvitation(be, do, aliceCli, faberMap,
                 syncedInviteAcceptedWithClaimsOut)
    return aliceCli


def testAliceAcceptFaberInvitationFirstTime(aliceAcceptedFaberInvitation):
    pass


def testPingFaber(be, do, aliceCli, faberMap,
                  aliceAcceptedFaberInvitation):
    be(aliceCli)
    do('ping {inviter}',
       within=3,
       expect=[
           "Ping sent.",
           "Pong received."],
       mapper=faberMap)


def testAliceAcceptFaberInvitationAgain(be, do, aliceCli, faberMap,
                                        unsycedAlreadyAcceptedInviteAcceptedOut,
                                        aliceAcceptedFaberInvitation):
    li = aliceCli.activeWallet.getLinkInvitationByTarget(faberMap['target'])
    li.linkStatus = None
    be(aliceCli)
    acceptInvitation(be, do, aliceCli, faberMap,
                     unsycedAlreadyAcceptedInviteAcceptedOut)
    li.linkStatus = constant.LINK_STATUS_ACCEPTED


# TODO: Write tests which sends request with invalid signature
# TODO: Write tests which receives response with invalid signature

def testShowFaberLinkAfterInviteAccept(be, do, aliceCli, faberMap,
                                       showAcceptedLinkOut,
                                       aliceAcceptedFaberInvitation):
    be(aliceCli)

    do("show link {inviter}", expect=showAcceptedLinkOut,
       # not_expect="Link (not yet accepted)",
       mapper=faberMap)


def testShowClaimNotExists(be, do, aliceCli, faberMap, showClaimNotFoundOut,
                                   aliceAcceptedFaberInvitation):
    be(aliceCli)

    do("show claim claim-to-show-not-exists",
       expect=showClaimNotFoundOut,
       mapper=faberMap,
       within=3)


def testShowTranscriptClaim(be, do, aliceCli, transcriptClaimMap,
                            showTranscriptClaimOut,
                            aliceAcceptedFaberInvitation):
    be(aliceCli)
    totalSchemasBefore = getTotalSchemas(aliceCli)
    do("show claim {name}",
       expect=showTranscriptClaimOut,
       mapper=transcriptClaimMap,
       within=3)
    assert totalSchemasBefore + 1 == getTotalSchemas(aliceCli)


def testReqClaimNotExists(be, do, aliceCli, faberMap, showClaimNotFoundOut,
                          aliceAcceptedFaberInvitation):
    be(aliceCli)

    do("request claim claim-to-req-not-exists",
       expect=showClaimNotFoundOut,
       mapper=faberMap)


@pytest.fixture(scope="module")
def aliceRequestedTranscriptClaim(be, do, aliceCli, transcriptClaimMap,
                                       reqClaimOut, preRequisite,
                                       aliceAcceptedFaberInvitation):
    be(aliceCli)
    totalClaimsRcvdBefore = getTotalClaimsRcvd(aliceCli)
    do("request claim {name}", within=5,
       expect=reqClaimOut,
       mapper=transcriptClaimMap)

    async def assertTotalClaimsRcvdIncreasedByOne():
        assert totalClaimsRcvdBefore + 1 == \
               len((await aliceCli.agent.prover.wallet.getAllClaims()).keys())

    aliceCli.looper.run(
        eventually(assertTotalClaimsRcvdIncreasedByOne, timeout=2))


def testAliceReqClaim(aliceRequestedTranscriptClaim):
    pass


def testShowFaberClaimPostReqClaim(be, do, aliceCli,
                                   aliceRequestedTranscriptClaim,
                                   transcriptClaimValueMap,
                                   rcvdTranscriptClaimOut):
    be(aliceCli)
    do("show claim {name}",
       expect=rcvdTranscriptClaimOut,
       mapper=transcriptClaimValueMap,
       within=3)


def testShowAcmeInvite(be, do, aliceCli, acmeMap):
    be(aliceCli)
    inviteContents = doubleBraces(getFileLines(acmeMap.get("invite")))

    do('show {invite}', expect=inviteContents,
       mapper=acmeMap)


@pytest.fixture(scope="module")
def acmeInviteLoadedByAlice(be, do, aliceCli, loadInviteOut, acmeMap):
    totalLinksBefore = getTotalLinks(aliceCli)
    be(aliceCli)
    do('load {invite}', expect=loadInviteOut, mapper=acmeMap)
    link = aliceCli.activeWallet.getLinkInvitation(acmeMap.get("inviter"))
    link.remoteEndPoint = acmeMap.get(ENDPOINT)
    assert totalLinksBefore + 1 == getTotalLinks(aliceCli)
    return aliceCli


def testLoadAcmeInvite(acmeInviteLoadedByAlice):
    pass


def testShowAcmeLink(be, do, aliceCli, acmeInviteLoadedByAlice,
                     showUnSyncedLinkOut, showLinkWithProofRequestsOut, acmeMap):
    showUnSyncedLinkWithClaimReqs = \
        showUnSyncedLinkOut + showLinkWithProofRequestsOut
    be(aliceCli)

    cp = acmeMap.copy()
    cp.update(last_synced='<this link has not yet been synchronized>')
    do('show link {inviter}', expect=showUnSyncedLinkWithClaimReqs, mapper=cp)


@pytest.fixture(scope="module")
def aliceAcceptedAcmeJobInvitation(aliceCli, be, do,
                                   unsycedAcceptedInviteWithoutClaimOut,
                                   preRequisite,
                                   aliceRequestedTranscriptClaim,
                                   acmeInviteLoadedByAlice,
                                   acmeMap):
    be(aliceCli)
    acceptInvitation(be, do, aliceCli, acmeMap,
                     unsycedAcceptedInviteWithoutClaimOut)
    return aliceCli


def testAliceAcceptAcmeJobInvitation(aliceAcceptedAcmeJobInvitation):
    pass


def testSetAttrWithoutContext(be, do, aliceCli):
    be(aliceCli)
    do("set first_name to Alice", expect=[
        "No context, "
        "use below command to "
        "set the context"])


def testShowAcmeLinkAfterInviteAccept(be, do, aliceCli, acmeMap,
                                      aliceAcceptedAcmeJobInvitation,
                                      showAcceptedLinkWithoutAvailableClaimsOut):
    be(aliceCli)

    do("show link {inviter}", expect=showAcceptedLinkWithoutAvailableClaimsOut,
       not_expect="Link (not yet accepted)",
       mapper=acmeMap)


def testShowProofRequestNotExists(be, do, aliceCli, acmeMap,
                                  proofRequestNotExists):
    be(aliceCli)
    do("show proof request proof-request-to-show-not-exists",
       expect=proofRequestNotExists,
       mapper=acmeMap,
       within=3)


def proofRequestShown(be, do, userCli, agentMap,
                      proofRequestOut,
                      proofRequestMap,
                      claimAttrValueMap):
    be(userCli)

    mapping = {
        "set-attr-first_name": "",
        "set-attr-last_name": "",
        "set-attr-phone_number": ""
    }
    mapping.update(agentMap)
    mapping.update(proofRequestMap)
    mapping.update(claimAttrValueMap)
    do("show proof request {proof-request-to-show}",
       expect=proofRequestOut,
       mapper=mapping,
       within=3)


def testShowJobAppClaimReqWithShortName(be, do, aliceCli, acmeMap,
                                        showJobAppProofRequestOut,
                                        jobApplicationProofRequestMap,
                                        transcriptClaimAttrValueMap,
                                        aliceAcceptedAcmeJobInvitation):
    newAcmeMap = {}
    newAcmeMap.update(acmeMap)
    newAcmeMap["proof-request-to-show"] = "Job"

    proofRequestShown(be, do, aliceCli, newAcmeMap,
                      showJobAppProofRequestOut,
                      jobApplicationProofRequestMap,
                      transcriptClaimAttrValueMap)


def testShowJobAppilcationProofRequest(be, do, aliceCli, acmeMap,
                                       showJobAppProofRequestOut,
                                       jobApplicationProofRequestMap,
                                       transcriptClaimAttrValueMap,
                                       aliceAcceptedAcmeJobInvitation):
    proofRequestShown(be, do, aliceCli, acmeMap,
                      showJobAppProofRequestOut,
                      jobApplicationProofRequestMap,
                      transcriptClaimAttrValueMap)


@pytest.fixture(scope="module")
def aliceSelfAttestsAttributes(be, do, aliceCli, acmeMap,
                               showJobAppProofRequestOut,
                               jobApplicationProofRequestMap,
                               transcriptClaimAttrValueMap,
                               aliceAcceptedAcmeJobInvitation):
    be(aliceCli)

    mapping = {
        "set-attr-first_name": "",
        "set-attr-last_name": "",
        "set-attr-phone_number": ""
    }
    mapping.update(acmeMap)
    mapping.update(jobApplicationProofRequestMap)
    mapping.update(transcriptClaimAttrValueMap)
    do("show proof request {proof-request-to-show}",
       expect=showJobAppProofRequestOut,
       mapper=mapping,
       within=3)
    do("set first_name to Alice")
    do("set last_name to Garcia")
    do("set phone_number to 123-555-1212")
    mapping.update({
        "set-attr-first_name": "Alice",
        "set-attr-last_name": "Garcia",
        "set-attr-phone_number": "123-555-1212"
    })
    return mapping


def testShowJobApplicationClaimReqAfterSetAttr(be, do, aliceCli,
                                               showJobAppProofRequestOut,
                                               aliceSelfAttestsAttributes):
    be(aliceCli)
    do("show proof request {proof-request-to-show}",
       expect=showJobAppProofRequestOut,
       mapper=aliceSelfAttestsAttributes,
       within=3)


# def testInvalidSigErrorResponse(be, do, aliceCli, faberMap,
#                                 preRequisite,
#                                 faberInviteSyncedWithoutEndpoint):
#
#     msg = {
#         f.REQ_ID.nm: getTimeBasedId(),
#         TYPE: ACCEPT_INVITE,
#         IDENTIFIER: faberMap['target'],
#         NONCE: "unknown"
#     }
#     signature = aliceCli.activeWallet.signMsg(msg,
#                                               aliceCli.activeWallet.defaultId)
#     msg[f.SIG.nm] = signature
#     link = aliceCli.activeWallet.getLink(faberMap['inviter'], required=True)
#     aliceCli.sendToAgent(msg, link)
#
#     be(aliceCli)
#     do(None,                        within=3,
#                                     expect=["Signature rejected.".
#                                                 format(msg)])
#
#
# def testLinkNotFoundErrorResponse(be, do, aliceCli, faberMap,
#                       faberInviteSyncedWithoutEndpoint):
#
#     msg = {
#         f.REQ_ID.nm: getTimeBasedId(),
#         TYPE: ACCEPT_INVITE,
#         IDENTIFIER: aliceCli.activeWallet.defaultId,
#         NONCE: "unknown"
#     }
#     signature = aliceCli.activeWallet.signMsg(msg,
#                                               aliceCli.activeWallet.defaultId)
#     msg[f.SIG.nm] = signature
#     link = aliceCli.activeWallet.getLink(faberMap['inviter'], required=True)
#     aliceCli.sendToAgent(msg, link)
#
#     be(aliceCli)
#     do(None, within=3,
#              expect=["Nonce not found".format(msg)])


def sendProof(be, do, userCli, agentMap, newAvailableClaims, extraMsgs=None):
    be(userCli)

    expectMsgs = [
        "Your Proof {proof-req-to-match} "
        "{claim-ver-req-to-show} was "
        "received and verified"
    ]
    if extraMsgs:
        expectMsgs.extend(extraMsgs)
    mapping = {}
    mapping.update(agentMap)
    if newAvailableClaims:
        mapping['new-available-claims'] = newAvailableClaims
        expectMsgs.append("Available Claim(s): {new-available-claims}")

    do("send proof {proof-req-to-match} to {inviter}",
       within=7,
       expect=expectMsgs,
       mapper=mapping)


@pytest.fixture(scope="module")
def jobApplicationClaimSent(be, do, aliceCli, acmeMap,
                            aliceAcceptedAcmeJobInvitation,
                            aliceRequestedTranscriptClaim,
                            aliceSelfAttestsAttributes):
    totalAvailableClaimsBefore = getTotalAvailableClaims(aliceCli)
    sendProof(be, do, aliceCli, acmeMap, "Job-Certificate")
    assert totalAvailableClaimsBefore + 1 == getTotalAvailableClaims(aliceCli)


def testAliceSendClaimProofToAcme(jobApplicationClaimSent):
    pass


# TODO: Need to uncomment below tests once above testAliceSendClaimProofToAcme
# test works correctly all the time and also we start supporting
# building and sending proofs from more than one claim

def testShowAcmeLinkAfterClaimSent(be, do, aliceCli, acmeMap,
                                   jobApplicationClaimSent,
                                   showAcceptedLinkWithAvailableClaimsOut):
    be(aliceCli)
    mapping = {}
    mapping.update(acmeMap)
    mapping["claims"] = "Job-Certificate"

    acmeMap.update(acmeMap)
    do("show link {inviter}", expect=showAcceptedLinkWithAvailableClaimsOut,
       mapper=mapping)


def testShowJobCertClaim(be, do, aliceCli, jobCertificateClaimMap,
                         showJobCertClaimOut,
                         jobApplicationClaimSent):
    be(aliceCli)
    totalSchemasBefore = getTotalSchemas(aliceCli)
    do("show claim {name}",
       within=2,
       expect=showJobCertClaimOut,
       mapper=jobCertificateClaimMap)
    assert totalSchemasBefore + 1 == getTotalSchemas(aliceCli)


@pytest.fixture(scope="module")
def jobCertClaimRequested(be, do, aliceCli, preRequisite,
                        jobCertificateClaimMap, reqClaimOut1,
                        jobApplicationClaimSent):

    def removeSchema():
        inviter = jobCertificateClaimMap["inviter"]
        links = aliceCli.activeWallet.getMatchingLinks(inviter)
        assert len(links) == 1
        faberId = links[0].remoteIdentifier
        name, version = jobCertificateClaimMap["name"], \
                        jobCertificateClaimMap["version"]
        aliceCli.activeWallet._schemas.pop((name, version, faberId))

    # Removing schema to check if it fetches the schema again or not
    # removeSchema()

    be(aliceCli)

    totalClaimsRcvdBefore = getTotalClaimsRcvd(aliceCli)
    do("request claim {name}", within=7,
       expect=reqClaimOut1,
       mapper=jobCertificateClaimMap)
    assert totalClaimsRcvdBefore + 1 == getTotalClaimsRcvd(aliceCli)


def testReqJobCertClaim(jobCertClaimRequested):
    pass


def testShowAcmeClaimPostReqClaim(be, do, aliceCli,
                                  jobCertClaimRequested,
                                  jobCertificateClaimValueMap,
                                  rcvdJobCertClaimOut):
    be(aliceCli)
    do("show claim {name}",
       expect=rcvdJobCertClaimOut,
       mapper=jobCertificateClaimValueMap,
       within=3)


@pytest.fixture(scope="module")
def thriftInviteLoadedByAlice(be, do, aliceCli, loadInviteOut, thriftMap,
                              jobCertClaimRequested,
                              preRequisite):
    be(aliceCli)
    totalLinksBefore = getTotalLinks(aliceCli)
    do('load {invite}', expect=loadInviteOut, mapper=thriftMap)
    assert totalLinksBefore + 1 == getTotalLinks(aliceCli)
    return aliceCli


def testAliceLoadedThriftLoanApplication(thriftInviteLoadedByAlice):
    pass


def testPingThriftBeforeSync(be, do, aliceCli, thriftMap,
                             thriftInviteLoadedByAlice):
    be(aliceCli)
    do('ping {inviter}', expect=['Ping sent.'], mapper=thriftMap)


@pytest.fixture(scope="module")
def aliceAcceptedThriftLoanApplication(be, do, aliceCli, thriftMap,
                                       connectedToTest,
                                       preRequisite,
                                       thriftInviteLoadedByAlice,
                                       syncedInviteAcceptedOutWithoutClaims):

    connectIfNotAlreadyConnected(do, connectedToTest, aliceCli, thriftMap)
    acceptInvitation(be, do, aliceCli, thriftMap,
                     syncedInviteAcceptedOutWithoutClaims)
    return aliceCli


def testAliceAcceptsThriftLoanApplication(aliceAcceptedThriftLoanApplication):
    pass


@pytest.fixture(scope="module")
def bankBasicClaimSent(be, do, aliceCli, thriftMap,
                       aliceAcceptedThriftLoanApplication):
    mapping = {}
    mapping.update(thriftMap)
    mapping["proof-req-to-match"] = "Loan-Application-Basic"
    extraMsgs = ["Loan eligibility criteria satisfied, "
                 "please send another claim 'Loan-Application-KYC'"]
    sendProof(be, do, aliceCli, mapping, None, extraMsgs)


def testAliceSendBankBasicClaim(bankBasicClaimSent):
    pass


@pytest.fixture(scope="module")
def bankKYCProofSent(be, do, aliceCli, thriftMap,
                     bankBasicClaimSent):
    mapping = {}
    mapping.update(thriftMap)
    mapping["proof-req-to-match"] = "Loan-Application-KYC"
    sendProof(be, do, aliceCli, mapping, None)


def restartCliAndTestWalletRestoration(be, do, cli, connectedToTest):
    be(cli)
    connectIfNotAlreadyConnected(do, connectedToTest, cli, {})
    do(None, expect=[
        'Saved keyring ',
        'Active keyring set to '
    ], within=5)
    assert cli._activeWallet is not None
    # assert len(cli._activeWallet._links) == 3
    # assert len(cli._activeWallet.identifiers) == 4


def testAliceSendBankKYCClaim(be, do, aliceCli, susanCli, bankKYCProofSent,
                              connectedToTest):
    be(aliceCli)
    exitFromCli(do)
    restartCliAndTestWalletRestoration(be, do, susanCli, connectedToTest)


def testAliceReqAvailClaimsFromNonExistentConnection(
        be, do, aliceCli, bankKYCProofSent, faberMap):
    be(aliceCli)
    do('request available claims from dummy-link', mapper=faberMap,
       expect=["No matching link invitations found in current keyring"])


def testAliceReqAvailClaimsFromFaber(
        be, do, aliceCli, bankKYCProofSent, faberMap):
    be(aliceCli)
    do('request available claims from {inviter}',
       mapper=faberMap,
       expect=["Available Claim(s): {claim-to-show}"],
       within=3)


def testAliceReqAvailClaimsFromAcme(
        be, do, aliceCli, bankKYCProofSent, acmeMap):
    be(aliceCli)
    do('request available claims from {inviter}',
       mapper=acmeMap,
       expect=["Available Claim(s): No available claims found"],
       within=3)