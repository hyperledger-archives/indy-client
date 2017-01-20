from copy import copy

import pytest

from plenum.common.signer_simple import SimpleSigner
from sovrin_client.test.cli.conftest import nymAddedOut


vals = {
    'newTrusteeIdr': SimpleSigner().identifier,
    'newTGBIdr': SimpleSigner().identifier,
    'newStewardIdr': SimpleSigner().identifier,
    'newSponsorIdr': SimpleSigner().identifier,
}


@pytest.fixture(scope="module")
def anotherTrusteeAdded(be, do, trusteeCli, nymAddedOut):
    global vals
    vals = copy(vals)
    vals['target'] = vals['newTrusteeIdr']
    be(trusteeCli)
    do('send NYM dest={newTrusteeIdr} role=TRUSTEE',
       within=5,
       expect=nymAddedOut, mapper=vals)


@pytest.fixture(scope="module")
def tbgAdded(be, do, trusteeCli, nymAddedOut):
    global vals
    vals = copy(vals)
    vals['target'] = vals['newTGBIdr']
    be(trusteeCli)
    do('send NYM dest={newTGBIdr} role=TGB',
       within=5,
       expect=nymAddedOut, mapper=vals)


@pytest.fixture(scope="module")
def stewardAdded(be, do, trusteeCli, nymAddedOut):
    global vals
    vals = copy(vals)
    vals['target'] = vals['newStewardIdr']
    be(trusteeCli)
    do('send NYM dest={newStewardIdr} role=STEWARD',
       within=5,
       expect=nymAddedOut, mapper=vals)


@pytest.fixture(scope="module")
def sponsorAdded(be, do, trusteeCli, nymAddedOut):
    global vals
    vals = copy(vals)
    vals['target'] = vals['newSponsorIdr']
    be(trusteeCli)
    do('send NYM dest={newSponsorIdr} role=SPONSOR',
       within=5,
       expect=nymAddedOut, mapper=vals)


def testTrusteeSuspendingSponsor(be, do, trusteeCli, sponsorAdded, nymAddedOut):
    be(trusteeCli)
    do('send NYM dest={newSponsorIdr} role=',
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
