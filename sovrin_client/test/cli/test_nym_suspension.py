from copy import copy

import pytest

from plenum.common.signer_simple import SimpleSigner
from sovrin_client.test.cli.conftest import nymAddedOut
from sovrin_common.roles import Roles

vals = {
    'newTrusteeIdr': [(s.identifier, s.seed) for s in [SimpleSigner()]][0],
    'newTGBIdr': [(s.identifier, s.seed) for s in [SimpleSigner()]][0],
    'newStewardIdr': [(s.identifier, s.seed) for s in [SimpleSigner()]][0],
    'newTrustAnchorIdr': [(s.identifier, s.seed) for s in [SimpleSigner()]][0],
}


@pytest.fixture(scope="module")
def anotherTrusteeAdded(be, do, trusteeCli, nymAddedOut):
    global vals
    v = copy(vals)
    v['target'] = vals['newTrusteeIdr'][0]
    be(trusteeCli)
    do('send NYM dest={{target}} role={role}'.format(role=Roles.TRUSTEE.name),
       within=5,
       expect=nymAddedOut, mapper=v)
    return v


@pytest.fixture(scope="module")
def tbgAdded(be, do, trusteeCli, nymAddedOut):
    global vals
    v = copy(vals)
    v['target'] = vals['newTGBIdr'][0]
    be(trusteeCli)
    do('send NYM dest={{target}} role={role}'.format(role=Roles.TGB.name),
       within=5,
       expect=nymAddedOut, mapper=v)
    return v


@pytest.fixture(scope="module")
def stewardAdded(be, do, trusteeCli, nymAddedOut):
    global vals
    v = copy(vals)
    v['target'] = vals['newStewardIdr'][0]
    be(trusteeCli)
    do('send NYM dest={{target}} role={role}'.format(role=Roles.STEWARD.name),
       within=5,
       expect=nymAddedOut, mapper=v)
    return v


@pytest.fixture(scope="module")
def trustAnchorAdded(be, do, trusteeCli, nymAddedOut):
    global vals
    v = copy(vals)
    v['target'] = vals['newTrustAnchorIdr'][0]
    be(trusteeCli)
    do('send NYM dest={{target}} role={role}'.format(role=Roles.TRUST_ANCHOR.name),
       within=5,
       expect=nymAddedOut, mapper=v)
    return v


# @pytest.yield_fixture(scope="module")
# def trustAnchorCLI(CliBuilder):
#     yield from CliBuilder("TrustAnchor")
#
#
# @pytest.fixture(scope="module")
# def trustAnchorCli(trustAnchorCLI, be, do, connectedToTest):
#     be(trustAnchorCLI)
#     do('connect test', within=3, expect=connectedToTest)
#     return trustAnchorCLI


def testTrusteeSuspendingTrustAnchor(be, do, trusteeCli, trustAnchorAdded,
                                     nymAddedOut, trustAnchorCli):
    be(trusteeCli)
    do('send NYM dest={target} role=',
       within=5,
       expect=nymAddedOut, mapper=trustAnchorAdded)
    # s = SimpleSigner().identifier
    # be(trustAnchorCli)
    # do('send NYM dest={target}',
    #    within=5,
    #    expect=nymAddedOut, mapper={'target': s})


def testTrusteeSuspendingSteward(be, do, trusteeCli, stewardAdded, nymAddedOut):
    be(trusteeCli)
    do('send NYM dest={target} role=',
       within=5,
       expect=nymAddedOut, mapper=stewardAdded)


def testTrusteeSuspendingTGB(be, do, trusteeCli, tbgAdded, nymAddedOut):
    be(trusteeCli)
    do('send NYM dest={target} role=',
       within=5,
       expect=nymAddedOut, mapper=tbgAdded)


def testTrusteeSuspendingTrustee(be, do, trusteeCli, anotherTrusteeAdded,
                                 nymAddedOut):
    be(trusteeCli)
    do('send NYM dest={target} role=',
       within=5,
       expect=nymAddedOut, mapper=anotherTrusteeAdded)
