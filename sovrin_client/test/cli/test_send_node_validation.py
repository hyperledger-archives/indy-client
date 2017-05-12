import pytest

from plenum.common.util import randomString
from sovrin_client.test.cli.conftest import newStewardCli


@pytest.fixture(scope='module')
def running_nodes(be, do, poolNodesStarted, trusteeCli, connectedToTest):
    pass


@pytest.yield_fixture(scope="module")
def cli_with_random_name(CliBuilder):
    yield from CliBuilder(randomString(6))


def new_steward_cli_fixture_args(be, do, poolNodesStarted, trusteeCli,
                  connectedToTest, nymAddedOut):
    return be, do, poolNodesStarted, trusteeCli, connectedToTest, nymAddedOut


def test_node_not_added_with_invalid_ip(running_nodes,
                                        new_steward_cli_fixture_args,
                                        cli_with_random_name):
    """
    Add a node with invalid ip, check the node is not part of the pool
    and also the cli indicates the failure
    :param running_nodes:
    :return:
    """
    # TOOD: Define new newNodeVals
    newStewardCli(*new_steward_cli_fixture_args, cli_with_random_name, newNodeVals)


def test_node_not_added_with_invalid_port(running_nodes,
                                          new_steward_cli_fixture_args,
                                          cli_with_random_name):
    """
    Add a node with invalid port, check the node is not part of the pool
    and also the cli indicates the failure
    """
    # TODO: take cue from above test
    pass


def test_node_not_added_with_invalid_dest(running_nodes,
                                          new_steward_cli_fixture_args,
                                          cli_with_random_name):
    """
    Add a node with invalid ip, check the node is not part of the pool
    and also the cli indicates the failure
    """
    # TODO: take cue from above test
    pass

