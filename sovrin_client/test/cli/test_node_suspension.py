from plenum.common.constants import SERVICES, VALIDATOR
from sovrin_client.test.cli.test_node import newStewardCli, newStewardCLI, \
    newNodeAdded, doNodeCmd, getNewNodeData


def testSuspendNode(be, do, trusteeCli, newNodeAdded):
    """
    Suspend a node and then cancel suspension. Suspend while suspended
    to test that there is no error
    """
    nodeData = newNodeAdded
    be(trusteeCli)
    nodeData['newNodeData'][SERVICES] = []
    doNodeCmd(do, nodeData=nodeData)
    # Re-suspend node
    nodeData['newNodeData'][SERVICES] = []
    doNodeCmd(do, nodeData=nodeData)

    # Cancel suspension
    nodeData['newNodeData'][SERVICES] = [VALIDATOR]
    doNodeCmd(do, nodeData=nodeData)

    # Re-cancel suspension
    nodeData['newNodeData'][SERVICES] = [VALIDATOR]
    doNodeCmd(do, nodeData=nodeData)

