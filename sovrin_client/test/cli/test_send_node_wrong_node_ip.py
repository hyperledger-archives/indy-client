import pytest
from plenum.common.constants import NODE_IP
from sovrin_common.roles import Roles

from sovrin_client.test.cli.helper import getNewNodeVals


def test_new_node_not_added_if_node_ip_incorrect(
        be, do, poolNodesStarted, trusteeCli, newStewardCli, nymAddedOut,
        newNodeVals):
    # Verify that "send NODE" command fails if node_ip is incorrect
    # (contains an odd space character at the end)
    be(newStewardCli)

    newNodeVals['newNodeData'][NODE_IP] += ' '

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
