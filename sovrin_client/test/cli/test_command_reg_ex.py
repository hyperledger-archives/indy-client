import pytest
from plenum.cli.helper import getClientGrams
from plenum.test.cli.helper import assertCliTokens
from plenum.test.cli.test_command_reg_ex import getMatchedVariables
from prompt_toolkit.contrib.regular_languages.compiler import compile

from sovrin_client.cli.helper import getNewClientGrams


@pytest.fixture("module")
def grammar():
    grams = getClientGrams() + getNewClientGrams()
    return compile("".join(grams))


def testSendNymWithRole(grammar):
    dest="LNAyBZUjvLF7duhrNtOWgdAKs18nHdbJUxJLT39iEGU="
    role="SPONSOR"
    matchedVars = getMatchedVariables(
        grammar, "send NYM dest={} role={}".format(dest, role))
    assertCliTokens(matchedVars, {
        "send_nym": "send NYM", "dest_id": dest, "role": role})


def testSendNymWithoutRole(grammar):
    dest="LNAyBZUjvLF7duhrNtOWgdAKs18nHdbJUxJLT39iEGU="
    matchedVars = getMatchedVariables(grammar, 'send NYM dest={}'.format(dest))
    assertCliTokens(matchedVars, {
        "send_nym": "send NYM", "dest_id": dest})


def testSendNymWithVerkey(grammar):
    dest="LNAyBZUjvLF7duhrNtOWgdAKs18nHdbJUxJLT39iEGU="
    role="SPONSOR"
    verkey="LNAyBZUjvLF7duhrNtOWgdAKs18nHdbJUxJLT39iEGU="
    matchedVars = getMatchedVariables(
        grammar, "send NYM dest={} role={} verkey={}".
            format(dest, role, verkey))
    assertCliTokens(matchedVars, {
        "send_nym": "send NYM", "dest_id": dest,
        "role": role, "new_ver_key": verkey
    })


def testSendAttribRegEx(grammar):
    dest = "LNAyBZUjvLF7duhrNtOWgdAKs18nHdbJUxJLT39iEGU="
    raw = '{"legal org": "BRIGHAM YOUNG UNIVERSITY, PROVO, UT", ' \
          '"email": "mail@byu.edu"}'
    matchedVars = getMatchedVariables(grammar,
                        'send ATTRIB dest={} raw={}'.format(dest, raw))
    assertCliTokens(matchedVars, {
        "send_attrib": "send ATTRIB", "dest_id": dest, "raw": raw})


def testAddAttrRegEx(grammar):
    getMatchedVariables(grammar,
                        "add attribute first_name=Tyler,last_name=Ruff,birth_date=12/17/1991,undergrad=True,postgrad=True,expiry_date=12/31/2101 for Tyler")


def testAddAttrProverRegEx(grammar):
    getMatchedVariables(grammar,
                        "attribute known to BYU first_name=Tyler, last_name=Ruff, birth_date=12/17/1991, undergrad=True, postgrad=True, expiry_date=12/31/2101")


def testSendIssuerKeyRegEx(grammar):
    getMatchedVariables(grammar, "send ISSUER_KEY ref=15")


def testShowFileCommandRegEx(grammar):
    matchedVars = getMatchedVariables(grammar,
                                      "show sample/faber-invitation.sovrin")
    assertCliTokens(matchedVars, {
        "show_file": "show", "file_path": "sample/faber-invitation.sovrin"})

    matchedVars = getMatchedVariables(grammar,
                                      "show sample/faber-invitation.sovrin ")
    assertCliTokens(matchedVars, {
        "show_file": "show", "file_path": "sample/faber-invitation.sovrin"})


def testLoadFileCommandRegEx(grammar):
    matchedVars = getMatchedVariables(grammar,
                                      "load sample/faber-invitation.sovrin")
    assertCliTokens(matchedVars, {
        "load_file": "load", "file_path": "sample/faber-invitation.sovrin"})

    matchedVars = getMatchedVariables(grammar,
                                      "load sample/faber-invitation.sovrin ")
    assertCliTokens(matchedVars, {
        "load_file": "load", "file_path": "sample/faber-invitation.sovrin"})


def testShowLinkRegEx(grammar):
    matchedVars = getMatchedVariables(grammar, "show link faber")
    assertCliTokens(matchedVars, {"show_link": "show link",
                                  "link_name": "faber"})

    matchedVars = getMatchedVariables(grammar, "show link faber college")
    assertCliTokens(matchedVars, {"show_link": "show link",
                                  "link_name": "faber college"})

    matchedVars = getMatchedVariables(grammar, "show link faber college ")
    assertCliTokens(matchedVars, {"show_link": "show link",
                                  "link_name": "faber college "})


def testConnectRegEx(grammar):
    getMatchedVariables(grammar, "connect dummy")
    getMatchedVariables(grammar, "connect test")
    getMatchedVariables(grammar, "connect live")


def testSyncLinkRegEx(grammar):
    matchedVars = getMatchedVariables(grammar, "sync faber")
    assertCliTokens(matchedVars, {"sync_link": "sync", "link_name": "faber"})

    matchedVars = getMatchedVariables(grammar, 'sync "faber"')
    assertCliTokens(matchedVars, {"sync_link": "sync", "link_name": '"faber"'})

    matchedVars = getMatchedVariables(grammar, 'sync "faber" ')
    assertCliTokens(matchedVars, {"sync_link": "sync", "link_name": '"faber" '})


def testPingTargetRegEx(grammar):
    matchedVars = getMatchedVariables(grammar, "ping faber")
    assertCliTokens(matchedVars, {"ping": "ping", "target_name": "faber"})


def testAcceptInvitationLinkRegEx(grammar):
    matchedVars = getMatchedVariables(grammar, "accept invitation from faber")
    assertCliTokens(matchedVars, {"accept_link_invite": "accept invitation from",
                                  "link_name": "faber"})

    matchedVars = getMatchedVariables(grammar, 'accept invitation from "faber"')
    assertCliTokens(matchedVars, {"accept_link_invite": "accept invitation from",
                                  "link_name": '"faber"'})

    matchedVars = getMatchedVariables(grammar, 'accept invitation from "faber" ')
    assertCliTokens(matchedVars, {"accept_link_invite": "accept invitation from",
                                  "link_name": '"faber" '})


def testShowClaimRegEx(grammar):
    matchedVars = getMatchedVariables(grammar, "show claim Transcript")
    assertCliTokens(matchedVars, {"show_claim": "show claim",
                                  "claim_name": "Transcript"})

    matchedVars = getMatchedVariables(grammar, 'show claim "Transcript"')
    assertCliTokens(matchedVars, {"show_claim": "show claim",
                                  "claim_name": '"Transcript"'})


def testRequestClaimRegEx(grammar):
    matchedVars = getMatchedVariables(grammar, "request claim Transcript")
    assertCliTokens(matchedVars, {"req_claim": "request claim",
                                  "claim_name": "Transcript"})

    matchedVars = getMatchedVariables(grammar, 'request claim "Transcript"')
    assertCliTokens(matchedVars, {"req_claim": "request claim",
                                  "claim_name": '"Transcript"'})


def testClaimReqRegEx(grammar):
    matchedVars = getMatchedVariables(grammar,
                                      "show claim request Job-Application")
    assertCliTokens(matchedVars, {"show_claim_req": "show claim request",
                                  "claim_req_name": "Job-Application"})

    matchedVars = getMatchedVariables(grammar,
                                      "show claim request Job-Application ")
    assertCliTokens(matchedVars, {"show_claim_req": "show claim request",
                                  "claim_req_name": "Job-Application "})


def testSetAttribute(grammar):
    matchedVars = getMatchedVariables(
        grammar, "set first_name to Alice")
    assertCliTokens(matchedVars, {
        "set_attr": "set", "attr_name": "first_name", "attr_value": "Alice"})


def testSendClaim(grammar):
    getMatchedVariables(grammar, 'send claim Job-Application to Acme')


def testSendPoolUpgrade(grammar):
    # Testing for start
    getMatchedVariables(grammar, "send POOL_UPGRADE name=upgrade-13 "
                                 "version=0.0.6 sha256=aad1242 action=start "
                                 "schedule={'AtDfpKFe1RPgcr5nnYBw1Wxkgyn8Zjyh5MzFoEUTeoV3': "
                                 "'2017-01-25T12:49:05.258870+00:00', "
                                 "'4yC546FFzorLPgTNTc6V43DnpFrR8uHvtunBxb2Suaa2': "
                                 "'2017-01-25T12:33:53.258870+00:00', "
                                 "'JpYerf4CssDrH76z7jyQPJLnZ1vwYgvKbvcp16AB5RQ': "
                                 "'2017-01-25T12:44:01.258870+00:00', "
                                 "'DG5M4zFm33Shrhjj6JB7nmx9BoNJUq219UXDfvwBDPe2': "
                                 "'2017-01-25T12:38:57.258870+00:00'} "
                                 "timeout=10")

    # Testing for cancel
    getMatchedVariables(grammar, 'send POOL_UPGRADE name=upgrade-13 version=0.0.6 '
                                 'sha256=aad1242 action=cancel '
                                 'justification="not gonna give you"')


def testDisconnect(grammar):
    matchedVars = getMatchedVariables(
        grammar, "disconnect")
    assertCliTokens(matchedVars, {"disconn": "disconnect"})


def testNewIdentifier(grammar):
    matchedVars = getMatchedVariables(
        grammar, "new identifier")
    assertCliTokens(matchedVars, {"new_id": "new identifier",
                                  "id_or_abbr_or_crypto": None,
                                  "seed": None, "alias": None})

    matchedVars = getMatchedVariables(
        grammar, "new identifier as myalis")
    assertCliTokens(matchedVars,
                    {"new_id": "new identifier", "id_or_abbr_or_crypto": None,
                     "seed": None, "alias": "myalis"})


    matchedVars = getMatchedVariables(
        grammar, "new identifier abbr")
    assertCliTokens(matchedVars, {"new_id": "new identifier", "id_or_abbr_or_crypto": "abbr",
                                  "seed": None, "alias": None})

    matchedVars = getMatchedVariables(
        grammar, "new identifier 4QxzWk3ajdnEA37NdNU5Kt")
    assertCliTokens(matchedVars, {"new_id": "new identifier",
                                  "id_or_abbr_or_crypto": "4QxzWk3ajdnEA37NdNU5Kt",
                                  "seed": None, "alias": None})

    matchedVars = getMatchedVariables(
        grammar, "new identifier 4QxzWk3ajdnEA37NdNU5Kt "
                 "with seed aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    assertCliTokens(matchedVars, {"new_id": "new identifier",
                                  "id_or_abbr_or_crypto": "4QxzWk3ajdnEA37NdNU5Kt",
                                  "seed": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                                  "alias": None})

    matchedVars = getMatchedVariables(
        grammar,
        "new identifier abbr with seed aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    assertCliTokens(matchedVars, {"new_id": "new identifier",
                                  "id_or_abbr_or_crypto": "abbr",
                                  "seed": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                                  "alias": None})

    matchedVars = getMatchedVariables(
        grammar,
        "new identifier crypto with seed aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    assertCliTokens(matchedVars, {"new_id": "new identifier",
                                  "id_or_abbr_or_crypto": "crypto",
                                  "seed": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                                  "alias": None})

    matchedVars = getMatchedVariables(
        grammar,
        "new identifier crypto with seed aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa as myalias")
    assertCliTokens(matchedVars, {"new_id": "new identifier",
                                  "id_or_abbr_or_crypto": "crypto",
                                  "seed": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                                  "alias": "myalias"})