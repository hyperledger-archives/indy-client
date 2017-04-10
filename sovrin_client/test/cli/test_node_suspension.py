from plenum.common.constants import SERVICES, VALIDATOR, TARGET_NYM, DATA
from plenum.common.signer_simple import SimpleSigner
from sovrin_client.test.cli.test_node import newStewardCli, newStewardCLI, \
    newNodeAdded, doNodeCmd, getNewNodeData
from sovrin_common.roles import Roles
from stp_core.network.port_dispenser import genHa


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


def testSuspendNodeWhichWasNeverActive(be, do, trusteeCli, nymAddedOut,
                                       poolNodesStarted, trusteeMap):
    """
    Add a node without services field and check that the ledger does not
    contain the `services` field and check that it can be blacklisted and
    the ledger has `services` as empty list
    """
    newStewardSeed = '0000000000000000000KellySteward2'
    newStewardIdr = 'DqCx7RFEpSUMZbV2mH89XPH6JT3jMvDNU55NTnBHsQCs'
    be(trusteeCli)
    do('send NYM dest={{remote}} role={role}'.format(
        role=Roles.STEWARD.name),
       within=5,
       expect=nymAddedOut, mapper={'remote': newStewardIdr})
    do('new key with seed {}'.format(newStewardSeed))
    nport, cport = (_[1] for _ in genHa(2))
    nodeId = '6G9QhQa3HWjRKeRmEvEkLbWWf2t7cw6KLtafzi494G4G'
    nodeData = {
        'newNodeIdr': nodeId,
        'newNodeData': {'client_port': cport,
                        'client_ip': '127.0.0.1',
                        'alias': 'Node6',
                        'node_ip': '127.0.0.1',
                        'node_port': nport
                        }
    }
    doNodeCmd(do, nodeData=nodeData)

    for node in poolNodesStarted.nodes.values():
        txn = list(node.poolLedger.getAllTxn().values())[-1]
        assert txn[TARGET_NYM] == nodeId
        assert SERVICES not in txn[DATA]

    do('new key with seed {}'.format(trusteeMap['trusteeSeed']))
    nodeData['newNodeData'][SERVICES] = []
    doNodeCmd(do, nodeData=nodeData)

    for node in poolNodesStarted.nodes.values():
        txn = list(node.poolLedger.getAllTxn().values())[-1]
        assert txn[TARGET_NYM] == nodeId
        assert SERVICES in txn[DATA] and txn[DATA][SERVICES] == []
