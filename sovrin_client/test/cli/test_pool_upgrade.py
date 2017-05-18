from copy import copy, deepcopy

import pytest

from sovrin_node.test import waits
from stp_core.loop.eventually import eventually
from plenum.common.constants import VERSION
from sovrin_common.constants import ACTION, CANCEL, JUSTIFICATION
from sovrin_node.test.upgrade.helper import checkUpgradeScheduled, \
    checkNoUpgradeScheduled
from sovrin_node.test.upgrade.conftest import validUpgrade


def send_upgrade_cmd(do, expect, upgrade_data):
    do('send POOL_UPGRADE name={name} version={version} sha256={sha256} '
       'action={action} schedule={schedule} timeout={timeout}',
       within=10,
       expect=expect, mapper=upgrade_data)


@pytest.fixture(scope='module')
def nodeIds(poolNodesStarted):
    return next(iter(poolNodesStarted.nodes.values())).poolManager.nodeIds


@pytest.fixture(scope="module")
def poolUpgradeSubmitted(be, do, trusteeCli, validUpgrade):
    be(trusteeCli)
    send_upgrade_cmd(do, ['Sending pool upgrade', 'Pool upgrade successful'],
                     validUpgrade)


@pytest.fixture(scope="module")
def poolUpgradeScheduled(poolUpgradeSubmitted, poolNodesStarted, validUpgrade):
    nodes = poolNodesStarted.nodes.values()
    timeout = waits.expectedUpgradeScheduled()
    poolNodesStarted.looper.run(
        eventually(checkUpgradeScheduled, nodes,
                   validUpgrade[VERSION], retryWait=1, timeout=timeout))


@pytest.fixture(scope="module")
def poolUpgradeCancelled(poolUpgradeScheduled, be, do, trusteeCli,
                         validUpgrade):
    validUpgrade = copy(validUpgrade)
    validUpgrade[ACTION] = CANCEL
    validUpgrade[JUSTIFICATION] = '"not gonna give you one"'
    be(trusteeCli)
    do('send POOL_UPGRADE name={name} version={version} sha256={sha256} '
       'action={action} justification={justification}',
       within=10,
       expect=['Sending pool upgrade', 'Pool upgrade successful'],
       mapper=validUpgrade)


def test_pool_upgrade_rejected(be, do, newStewardCli, validUpgrade):
    """
    Pool upgrade done by a non trustee is rejected
    """
    be(newStewardCli)
    send_upgrade_cmd(do,
                     ['Sending pool upgrade',
                      "Pool upgrade failed: client request invalid: UnauthorizedClientRequest('STEWARD cannot do POOL_UPGRADE'"],
                     validUpgrade)


def testPoolUpgradeSent(poolUpgradeScheduled):
    pass


def testPoolUpgradeCancelled(poolUpgradeCancelled, poolNodesStarted):
    nodes = poolNodesStarted.nodes.values()
    timeout = waits.expectedNoUpgradeScheduled()
    poolNodesStarted.looper.run(
        eventually(checkNoUpgradeScheduled,
                   nodes, retryWait=1, timeout=timeout))
