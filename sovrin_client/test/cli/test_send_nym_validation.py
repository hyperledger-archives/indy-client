import pytest
from libnacl import randombytes

from plenum.common.signer_did import DidSigner
from plenum.common.signer_simple import SimpleSigner
from plenum.common.util import rawToFriendly, friendlyToHexStr, friendlyToHex, \
    hexToFriendly
from sovrin_common.roles import Roles

NYM_ADDED_OUT = 'Nym {dest} added'
ERROR = 'Error:'
INVALID_SYNTAX = "Invalid syntax"


def createUuidIdentifier():
    return rawToFriendly(randombytes(16))


def createUuidIdentifierAndFullVerkey():
    didSigner = DidSigner(identifier=createUuidIdentifier())
    return didSigner.identifier, didSigner.verkey


def createHalfKeyIdentifierAndAbbrevVerkey():
    didSigner = DidSigner()
    return didSigner.identifier, didSigner.verkey


def createCryptonym():
    return SimpleSigner().identifier


def testSendNymSucceedsForUuidIdentifierAndOmittedVerkey(
        be, do, poolNodesStarted, trusteeCli):

    parameters = {
        'dest': createUuidIdentifier(),
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role}',
       mapper=parameters, expect=NYM_ADDED_OUT, within=2)


def testSendNymSucceedsForUuidIdentifierAndEmptyVerkey(
        be, do, poolNodesStarted, trusteeCli):

    parameters = {
        'dest': createUuidIdentifier(),
        'verkey': '',
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role} verkey={verkey}',
       mapper=parameters, expect=NYM_ADDED_OUT, within=2)


def testSendNymSucceedsForUuidIdentifierAndFullVerkey(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier, fullVerkey = createUuidIdentifierAndFullVerkey()

    parameters = {
        'dest': uuidIdentifier,
        'verkey': fullVerkey,
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role} verkey={verkey}',
       mapper=parameters, expect=NYM_ADDED_OUT, within=2)


def testSendNymSucceedsForHalfKeyIdentifierAndAbbrevVerkey(
        be, do, poolNodesStarted, trusteeCli):

    halfKeyIdentifier, abbrevVerkey = createHalfKeyIdentifierAndAbbrevVerkey()

    parameters = {
        'dest': halfKeyIdentifier,
        'verkey': abbrevVerkey,
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role} verkey={verkey}',
       mapper=parameters, expect=NYM_ADDED_OUT, within=2)


def testSendNymSucceedsForCryptonymIdentifierAndOmittedVerkey(
        be, do, poolNodesStarted, trusteeCli):

    parameters = {
        'dest': createCryptonym(),
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role}',
       mapper=parameters, expect=NYM_ADDED_OUT, within=2)


def testSendNymSucceedsForCryptonymIdentifierAndEmptyVerkey(
        be, do, poolNodesStarted, trusteeCli):

    parameters = {
        'dest': createCryptonym(),
        'verkey': '',
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role} verkey={verkey}',
       mapper=parameters, expect=NYM_ADDED_OUT, within=2)


def testSendNymSucceedsForCryptonymIdentifierAndSameFullVerkey(
        be, do, poolNodesStarted, trusteeCli):

    cryptonym = createCryptonym()

    parameters = {
        'dest': cryptonym,
        'verkey': cryptonym,
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role} verkey={verkey}',
       mapper=parameters, expect=NYM_ADDED_OUT, within=2)


def testSendNymSucceedsForCryptonymIdentifierAndDifferentFullVerkey(
        be, do, poolNodesStarted, trusteeCli):

    cryptonym = createCryptonym()
    _, fullVerkey = createUuidIdentifierAndFullVerkey()

    parameters = {
        'dest': cryptonym,
        'verkey': fullVerkey,
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role} verkey={verkey}',
       mapper=parameters, expect=NYM_ADDED_OUT, within=2)


def testSendNymSucceedsForTrusteeRole(
        be, do, poolNodesStarted, trusteeCli):

    halfKeyIdentifier, abbrevVerkey = createHalfKeyIdentifierAndAbbrevVerkey()

    parameters = {
        'dest': halfKeyIdentifier,
        'verkey': abbrevVerkey,
        'role': Roles.TRUSTEE.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role} verkey={verkey}',
       mapper=parameters, expect=NYM_ADDED_OUT, within=2)


def testSendNymSucceedsForStewardRole(
        be, do, poolNodesStarted, trusteeCli):

    halfKeyIdentifier, abbrevVerkey = createHalfKeyIdentifierAndAbbrevVerkey()

    parameters = {
        'dest': halfKeyIdentifier,
        'verkey': abbrevVerkey,
        'role': Roles.STEWARD.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role} verkey={verkey}',
       mapper=parameters, expect=NYM_ADDED_OUT, within=2)


def testSendNymSucceedsForTgbRole(
        be, do, poolNodesStarted, trusteeCli):

    halfKeyIdentifier, abbrevVerkey = createHalfKeyIdentifierAndAbbrevVerkey()

    parameters = {
        'dest': halfKeyIdentifier,
        'verkey': abbrevVerkey,
        'role': Roles.TGB.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role} verkey={verkey}',
       mapper=parameters, expect=NYM_ADDED_OUT, within=2)


def testSendNymSucceedsForTrustAnchorRole(
        be, do, poolNodesStarted, trusteeCli):

    halfKeyIdentifier, abbrevVerkey = createHalfKeyIdentifierAndAbbrevVerkey()

    parameters = {
        'dest': halfKeyIdentifier,
        'verkey': abbrevVerkey,
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role} verkey={verkey}',
       mapper=parameters, expect=NYM_ADDED_OUT, within=2)


def testSendNymSucceedsForOmittedRole(
        be, do, poolNodesStarted, trusteeCli):

    halfKeyIdentifier, abbrevVerkey = createHalfKeyIdentifierAndAbbrevVerkey()

    parameters = {
        'dest': halfKeyIdentifier,
        'verkey': abbrevVerkey
    }

    be(trusteeCli)
    do('send NYM dest={dest} verkey={verkey}',
       mapper=parameters, expect=NYM_ADDED_OUT, within=2)


def testSendNymSucceedsForEmptyRole(
        be, do, poolNodesStarted, trusteeCli):

    halfKeyIdentifier, abbrevVerkey = createHalfKeyIdentifierAndAbbrevVerkey()

    parameters = {
        'dest': halfKeyIdentifier,
        'verkey': abbrevVerkey,
        'role': ''
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role} verkey={verkey}',
       mapper=parameters, expect=NYM_ADDED_OUT, within=2)


@pytest.mark.skip(reason='SOV-1117')
def testSendNymFailsForCryptonymIdentifierAndMatchedAbbrevVerkey(
        be, do, poolNodesStarted, trusteeCli):

    cryptonym = createCryptonym()
    hexCryptonym = friendlyToHex(cryptonym)
    abbrevVerkey = '~' + hexToFriendly(hexCryptonym[16:])

    parameters = {
        'dest': cryptonym,
        'verkey': abbrevVerkey,
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role} verkey={verkey}',
       mapper=parameters, expect=ERROR, within=2)


@pytest.mark.skip(reason='SOV-1117')
def testSendNymFailsForCryptonymIdentifierAndUnmatchedAbbrevVerkey(
        be, do, poolNodesStarted, trusteeCli):

    cryptonym = createCryptonym()
    _, abbrevVerkey = createHalfKeyIdentifierAndAbbrevVerkey()

    parameters = {
        'dest': cryptonym,
        'verkey': abbrevVerkey,
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role} verkey={verkey}',
       mapper=parameters, expect=ERROR, within=2)


@pytest.mark.skip(reason='SOV-1108')
def testSendNymFailsIfIdentifierSizeIs15Bytes(
        be, do, poolNodesStarted, trusteeCli):

    parameters = {
        'dest': rawToFriendly(randombytes(15)),
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role}',
       mapper=parameters, expect=ERROR, within=2)


@pytest.mark.skip(reason='SOV-1108')
def testSendNymFailsIfIdentifierSizeIs17Bytes(
        be, do, poolNodesStarted, trusteeCli):

    parameters = {
        'dest': rawToFriendly(randombytes(17)),
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role}',
       mapper=parameters, expect=ERROR, within=2)


@pytest.mark.skip(reason='SOV-1108')
def testSendNymFailsIfFullVerkeySizeIs31Bytes(
        be, do, poolNodesStarted, trusteeCli):

    parameters = {
        'dest': rawToFriendly(randombytes(16)),
        'verkey': rawToFriendly(randombytes(31)),
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role}',
       mapper=parameters, expect=ERROR, within=2)


@pytest.mark.skip(reason='SOV-1108')
def testSendNymFailsIfFullVerkeySizeIs33Bytes(
        be, do, poolNodesStarted, trusteeCli):

    parameters = {
        'dest': rawToFriendly(randombytes(16)),
        'verkey': rawToFriendly(randombytes(33)),
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role}',
       mapper=parameters, expect=ERROR, within=2)


@pytest.mark.skip(reason='SOV-1108')
def testSendNymFailsIfAbbrevVerkeySizeIs15Bytes(
        be, do, poolNodesStarted, trusteeCli):

    parameters = {
        'dest': rawToFriendly(randombytes(16)),
        'verkey': '~' + rawToFriendly(randombytes(15)),
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role}',
       mapper=parameters, expect=ERROR, within=2)


@pytest.mark.skip(reason='SOV-1108')
def testSendNymFailsIfAbbrevVerkeySizeIs17Bytes(
        be, do, poolNodesStarted, trusteeCli):

    parameters = {
        'dest': rawToFriendly(randombytes(16)),
        'verkey': '~' + rawToFriendly(randombytes(17)),
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role}',
       mapper=parameters, expect=ERROR, within=2)


@pytest.mark.skip(reason='SOV-1108')
def testSendNymFailsIfCryptonymSizeIs31Bytes(
        be, do, poolNodesStarted, trusteeCli):

    parameters = {
        'dest': rawToFriendly(randombytes(31)),
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role}',
       mapper=parameters, expect=ERROR, within=2)


@pytest.mark.skip(reason='SOV-1108')
def testSendNymFailsIfCryptonymSizeIs33Bytes(
        be, do, poolNodesStarted, trusteeCli):

    parameters = {
        'dest': rawToFriendly(randombytes(33)),
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role}',
       mapper=parameters, expect=ERROR, within=2)


@pytest.mark.skip(reason='SOV-1109')
def testSendNymFailsIfUuidIdentifierIsHexEncoded(
        be, do, poolNodesStarted, trusteeCli):

    parameters = {
        'dest': friendlyToHexStr(createUuidIdentifier()),
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role}',
       mapper=parameters, expect=ERROR, within=2)


@pytest.mark.skip(reason='SOV-1109')
def testSendNymFailsIfFullVerkeyIsHexEncoded(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier, fullVerkey = createUuidIdentifierAndFullVerkey()

    parameters = {
        'dest': uuidIdentifier,
        'verkey': friendlyToHexStr(fullVerkey),
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role} verkey={verkey}',
       mapper=parameters, expect=ERROR, within=2)


@pytest.mark.skip(reason='SOV-1109')
def testSendNymFailsIfAbbrevVerkeyIsHexEncoded(
        be, do, poolNodesStarted, trusteeCli):

    halfKeyIdentifier, abbrevVerkey = createHalfKeyIdentifierAndAbbrevVerkey()

    parameters = {
        'dest': halfKeyIdentifier,
        'verkey': '~' + friendlyToHexStr(abbrevVerkey.replace('~', '')),
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role} verkey={verkey}',
       mapper=parameters, expect=ERROR, within=2)


@pytest.mark.skip(reason='SOV-1109')
def testSendNymFailsIfCryptonymIsHexEncoded(
        be, do, poolNodesStarted, trusteeCli):

    parameters = {
        'dest': friendlyToHexStr(createCryptonym()),
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role}',
       mapper=parameters, expect=ERROR, within=2)


@pytest.mark.skip(reason='SOV-1109')
def testSendNymFailsIfIdentifierContainsNonBase58Characters(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()

    parameters = {
        'dest': uuidIdentifier[:5] + '/' + uuidIdentifier[6:],
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role}',
       mapper=parameters, expect=ERROR, within=2)


@pytest.mark.skip(reason='SOV-1109')
def testSendNymFailsIfFullVerkeyContainsNonBase58Characters(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier, fullVerkey = createUuidIdentifierAndFullVerkey()

    parameters = {
        'dest': uuidIdentifier,
        'verkey': fullVerkey[:5] + '/' + fullVerkey[6:],
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role} verkey={verkey}',
       mapper=parameters, expect=ERROR, within=2)


@pytest.mark.skip(reason='SOV-1109')
def testSendNymFailsIfAbbrevVerkeyContainsNonBase58Characters(
        be, do, poolNodesStarted, trusteeCli):

    halfKeyIdentifier, abbrevVerkey = createHalfKeyIdentifierAndAbbrevVerkey()

    parameters = {
        'dest': halfKeyIdentifier,
        'verkey': abbrevVerkey[:6] + '/' + abbrevVerkey[7:],
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role} verkey={verkey}',
       mapper=parameters, expect=ERROR, within=2)


@pytest.mark.skip(reason='SOV-1109')
def testSendNymFailsIfCryptonymContainsNonBase58Characters(
        be, do, poolNodesStarted, trusteeCli):

    cryptonym = createCryptonym()

    parameters = {
        'dest': cryptonym[:5] + '/' + cryptonym[6:],
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role}',
       mapper=parameters, expect=ERROR, within=2)


@pytest.mark.skip(reason='SOV-1109')
def testSendNymFailsIfFullVerkeyContainsTilde(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier, fullVerkey = createUuidIdentifierAndFullVerkey()

    parameters = {
        'dest': uuidIdentifier,
        'verkey': '~' + fullVerkey,
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role} verkey={verkey}',
       mapper=parameters, expect=ERROR, within=2)


@pytest.mark.skip(reason='SOV-1109')
def testSendNymFailsIfAbbrevVerkeyDoesNotContainTilde(
        be, do, poolNodesStarted, trusteeCli):

    halfKeyIdentifier, abbrevVerkey = createHalfKeyIdentifierAndAbbrevVerkey()

    parameters = {
        'dest': halfKeyIdentifier,
        'verkey': abbrevVerkey.replace('~', ''),
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role} verkey={verkey}',
       mapper=parameters, expect=ERROR, within=2)


@pytest.mark.skip(reason='SOV-1110')
def testSendNymFailsIfRoleIsUnknown(
        be, do, poolNodesStarted, trusteeCli):

    halfKeyIdentifier, abbrevVerkey = createHalfKeyIdentifierAndAbbrevVerkey()

    parameters = {
        'dest': halfKeyIdentifier,
        'verkey': abbrevVerkey,
        'role': 'SUPERVISOR'
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role} verkey={verkey}',
       mapper=parameters, expect=ERROR, within=2)


@pytest.mark.skip(reason='SOV-1110')
def testSendNymFailsIfRoleIsSpecifiedUsingNumericCode(
        be, do, poolNodesStarted, trusteeCli):

    halfKeyIdentifier, abbrevVerkey = createHalfKeyIdentifierAndAbbrevVerkey()

    parameters = {
        'dest': halfKeyIdentifier,
        'verkey': abbrevVerkey,
        'role': Roles.TRUST_ANCHOR.value
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role} verkey={verkey}',
       mapper=parameters, expect=ERROR, within=2)


@pytest.mark.skip(reason='SOV-1111')
def testSendNymHasInvalidSyntaxIfParametersOrderIsWrong(
        be, do, poolNodesStarted, trusteeCli):

    halfKeyIdentifier, abbrevVerkey = createHalfKeyIdentifierAndAbbrevVerkey()

    parameters = {
        'dest': halfKeyIdentifier,
        'verkey': abbrevVerkey,
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM verkey={verkey} role={role} dest={dest}',
       mapper=parameters, expect=INVALID_SYNTAX, within=2)


@pytest.mark.skip(reason='SOV-1111')
def testSendNymHasInvalidSyntaxIfIdentifierIsEmpty(
        be, do, poolNodesStarted, trusteeCli):

    _, fullVerkey = createUuidIdentifierAndFullVerkey()

    parameters = {
        'dest': '',
        'verkey': fullVerkey,
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role} verkey={verkey}',
       mapper=parameters, expect=INVALID_SYNTAX, within=2)


@pytest.mark.skip(reason='SOV-1111')
def testSendNymHasInvalidSyntaxIfIdentifierIsOmitted(
        be, do, poolNodesStarted, trusteeCli):

    _, fullVerkey = createUuidIdentifierAndFullVerkey()

    parameters = {
        'verkey': fullVerkey,
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM role={role} verkey={verkey}',
       mapper=parameters, expect=INVALID_SYNTAX, within=2)


@pytest.mark.skip(reason='SOV-1111')
def testSendNymHasInvalidSyntaxIfIdentifierAndVerkeyAreOmitted(
        be, do, poolNodesStarted, trusteeCli):

    parameters = {
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM role={role}',
       mapper=parameters, expect=INVALID_SYNTAX, within=2)


@pytest.mark.skip(reason='SOV-1111')
def testSendNymHasInvalidSyntaxIfUnknownParameterIsPassed(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier, fullVerkey = createUuidIdentifierAndFullVerkey()

    parameters = {
        'dest': uuidIdentifier,
        'verkey': fullVerkey,
        'role': Roles.TRUST_ANCHOR.name,
        'extra': 42
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role} verkey={verkey} extra={extra}',
       mapper=parameters, expect=INVALID_SYNTAX, within=2)


def testSendNymHasInvalidSyntaxIfAllParametersAreOmitted(
        be, do, poolNodesStarted, trusteeCli):

    be(trusteeCli)
    do('send NYM', expect=INVALID_SYNTAX, within=2)
