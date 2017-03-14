from copy import copy

import pytest
from plenum.common.roles import Roles

from plenum.common.signer_simple import SimpleSigner
from sovrin_client.test.cli.conftest import nymAddedOut


vals = {
    'newTrusteeIdr': SimpleSigner().identifier,
    'newTGBIdr': SimpleSigner().identifier,
    'newStewardIdr': SimpleSigner().identifier,
    'newTrustAnchorIdr': SimpleSigner().identifier,
}


@pytest.fixture(scope="module")
def anotherTrusteeAdded(be, do, trusteeCli, nymAddedOut):
    global vals
    vals = copy(vals)
    vals['target'] = vals['newTrusteeIdr']
    be(trusteeCli)
    do('send NYM dest={{newTrusteeIdr}} role={role}'.format(role=Roles.TRUSTEE.name),
       within=5,
       expect=nymAddedOut, mapper=vals)


@pytest.fixture(scope="module")
def tbgAdded(be, do, trusteeCli, nymAddedOut):
    global vals
    vals = copy(vals)
    vals['target'] = vals['newTGBIdr']
    be(trusteeCli)
    do('send NYM dest={{newTGBIdr}} role={role}'.format(role=Roles.TGB.name),
       within=5,
       expect=nymAddedOut, mapper=vals)


@pytest.fixture(scope="module")
def stewardAdded(be, do, trusteeCli, nymAddedOut):
    global vals
    vals = copy(vals)
    vals['target'] = vals['newStewardIdr']
    be(trusteeCli)
    do('send NYM dest={{newStewardIdr}} role={role}'.format(role=Roles.STEWARD.name),
       within=5,
       expect=nymAddedOut, mapper=vals)


@pytest.fixture(scope="module")
def trustAnchorAdded(be, do, trusteeCli, nymAddedOut):
    global vals
    vals = copy(vals)
    vals['target'] = vals['newTrustAnchorIdr']
    be(trusteeCli)
    do('send NYM dest={{newTrustAnchorIdr}} role={role}'.format(role=Roles.TRUST_ANCHOR.name),
       within=5,
       expect=nymAddedOut, mapper=vals)


def testTrusteeSuspendingTrustAnchor(be, do, trusteeCli, trustAnchorAdded, nymAddedOut):
    be(trusteeCli)
    do('send NYM dest={newTrustAnchorIdr} role=',
       within=5,
       expect=nymAddedOut, mapper=vals)


def testTrusteeSuspendingSteward(be, do, trusteeCli, stewardAdded, nymAddedOut):
    be(trusteeCli)
    do('send NYM dest={newStewardIdr} role=',
       within=5,
       expect=nymAddedOut, mapper=vals)


def testTrusteeSuspendingTGB(be, do, trusteeCli, tbgAdded, nymAddedOut):
    be(trusteeCli)
    do('send NYM dest={newTGBIdr} role=',
       within=5,
       expect=nymAddedOut, mapper=vals)


def testTrusteeSuspendingTrustee(be, do, trusteeCli, anotherTrusteeAdded,
                                 nymAddedOut):
    be(trusteeCli)
    do('send NYM dest={newTrusteeIdr} role=',
       within=5,
       expect=nymAddedOut, mapper=vals)
