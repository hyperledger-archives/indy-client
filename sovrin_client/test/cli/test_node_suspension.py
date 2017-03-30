from plenum.common.constants import SERVICES, VALIDATOR
from sovrin_client.test.cli.test_node import newStewardCli, newStewardCLI, \
    newNodeAdded, doNodeCmd, getNewNodeData


def testSuspendNode(be, do, trusteeCli, newNodeAdded):
    nodeData = newNodeAdded
    be(trusteeCli)
    nodeData['newNodeData'][SERVICES] = []
    doNodeCmd(do, nodeData=nodeData)
    nodeData['newNodeData'][SERVICES] = [VALIDATOR]
    doNodeCmd(do, nodeData=nodeData)

