from plenum.common.util import cryptonymToHex

from sovrin_client.test.cli.helper import getNewNodeVals
from sovrin_common.roles import Roles


def testNewNodeNotAddedIfHexKeyUsedInsteadOfBase58Key(
        be, do, poolNodesStarted, trusteeCli, newStewardCli, nymAddedOut,
        newNodeVals):
    # Verify that "send NODE" command fails if hex key is used
    # instead of base58 key
    be(newStewardCli)

    newNodeVals['newNodeIdr'] = cryptonymToHex(
        newNodeVals['newNodeIdr']).decode()

    do('send NODE dest={newNodeIdr} data={newNodeData}',
       within=8, expect=['Node request failed'], mapper=newNodeVals)

    # Verify that the pool is still operable
    be(trusteeCli)

    anotherNewNodeVals = getNewNodeVals()
    anotherNewNodeVals['remote'] = anotherNewNodeVals['newStewardIdr']
    anotherNewNodeVals['newStewardSeed'] = anotherNewNodeVals[
        'newStewardSeed'].decode()

    do('send NYM dest={{newStewardIdr}} role={role}'
       .format(role=Roles.STEWARD.name),
       within=3,
       expect=nymAddedOut, mapper=anotherNewNodeVals)
