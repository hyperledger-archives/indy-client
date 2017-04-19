from copy import copy

import pytest
from plenum.common import util

from plenum.test import waits
from stp_core.crypto.util import randomSeed
from stp_core.loop.eventually import eventually

from stp_core.network.port_dispenser import genHa
from plenum.common.signer_simple import SimpleSigner
from plenum.common.constants import NODE_IP, CLIENT_IP, CLIENT_PORT, NODE_PORT, \
    ALIAS, CLIENT_STACK_SUFFIX, SERVICES, VALIDATOR
from plenum.common.util import randomString
from plenum.test.cli.helper import exitFromCli
from sovrin_common.roles import Roles


def getNewNodeData():
    newStewardSeed = randomSeed()
    newNodeSeed = randomSeed()
    nodeIp, nodePort = genHa()
    clientIp, clientPort = genHa()

    newNodeData = {
        NODE_IP: nodeIp,
        NODE_PORT: nodePort,
        CLIENT_IP: clientIp,
        CLIENT_PORT: clientPort,
        ALIAS: randomString(6),
        SERVICES: [VALIDATOR]
    }

    return {
        'newStewardSeed': newStewardSeed,
        'newStewardIdr': SimpleSigner(seed=newStewardSeed).identifier,
        'newNodeSeed': newNodeSeed,
        'newNodeIdr': SimpleSigner(seed=newNodeSeed).identifier,
        'newNodeData': newNodeData
    }


vals = getNewNodeData()


@pytest.yield_fixture(scope="module")
def newStewardCLI(CliBuilder):
    yield from CliBuilder("newSteward")


@pytest.fixture(scope="module")
def newStewardCli(be, do, poolNodesStarted, trusteeCli,
                  connectedToTest, nymAddedOut, newStewardCLI):
    be(trusteeCli)
    if not trusteeCli._isConnectedToAnyEnv():
        do('connect test', within=3,
           expect=connectedToTest)

    global vals
    v = copy(vals)
    v['target'] = v['newStewardIdr']
    v['newStewardSeed'] = v['newStewardSeed'].decode()

    do('send NYM dest={{newStewardIdr}} role={role}'.format(role=Roles.STEWARD.name),
       within=3,
       expect=nymAddedOut, mapper=v)

    be(newStewardCLI)

    do('new key with seed {newStewardSeed}', expect=[
        'Identifier for key is {newStewardIdr}',
        'Current identifier set to {newStewardIdr}'],
       mapper=v)

    if not newStewardCLI._isConnectedToAnyEnv():
        do('connect test', within=3,
           expect=connectedToTest)

    return newStewardCLI


def doNodeCmd(do, nodeData=None, expMsgs=None):
    mapper = nodeData or vals
    expect = expMsgs or ['Node request completed']
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       within=8, expect=expect, mapper=mapper)


@pytest.fixture(scope="module")
def tconf(tconf, request):
    oldVal = tconf.UpdateGenesisPoolTxnFile
    tconf.UpdateGenesisPoolTxnFile = True

    def reset():
        tconf.UpdateGenesisPoolTxnFile = oldVal

    request.addfinalizer(reset)
    return tconf


@pytest.fixture(scope="module")
def newNodeAdded(be, do, poolNodesStarted, philCli, newStewardCli, connectedToTest):
    be(philCli)

    if not philCli._isConnectedToAnyEnv():
        do('connect test', within=3,
           expect=connectedToTest)

    be(newStewardCli)
    doNodeCmd(do)
    newNodeData = vals["newNodeData"]

    def checkClientConnected(client):
        name = newNodeData[ALIAS] + CLIENT_STACK_SUFFIX
        assert name in client.nodeReg

    def checkNodeConnected(nodes):
        for node in nodes:
            name = newNodeData[ALIAS]
            assert name in node.nodeReg
    timeout = waits.expectedClientConnectionTimeout(
        util.getMaxFailures(len(philCli.nodeReg))
    )
    newStewardCli.looper.run(eventually(checkClientConnected,
                                        newStewardCli.activeClient,
                                        timeout=timeout))
    timeout = waits.expectedClientConnectionTimeout(
        util.getMaxFailures(len(philCli.nodeReg))
    )
    philCli.looper.run(eventually(checkClientConnected,
                                  philCli.activeClient,
                                  timeout=timeout))

    timeout = waits.expectedClientConnectionTimeout(
        util.getMaxFailures(len(philCli.nodeReg))
    )
    poolNodesStarted.looper.run(eventually(checkNodeConnected,
                                           list(poolNodesStarted.nodes.values()),
                                           timeout=timeout))
    return vals


def testAddNewNode(newNodeAdded):
    pass


def testConsecutiveAddSameNodeWithoutAnyChange(be, do, newStewardCli,
                                               newNodeAdded):
    be(newStewardCli)
    doNodeCmd(do, expMsgs=['node already has the same data as requested'])
    exitFromCli(do)


def testConsecutiveAddSameNodeWithNodeAndClientPortSame(be, do, newStewardCli,
                                                        newNodeAdded):
    be(newStewardCli)
    nodeIp, nodePort = genHa()
    vals['newNodeData'][NODE_IP] = nodeIp
    vals['newNodeData'][NODE_PORT] = nodePort
    vals['newNodeData'][CLIENT_IP] = nodeIp
    vals['newNodeData'][CLIENT_PORT] = nodePort
    doNodeCmd(do, nodeData=vals,
              expMsgs=['node and client ha cannot be same'])
    exitFromCli(do)


def testConsecutiveAddSameNodeWithNonAliasChange(be, do, newStewardCli,
                                                 newNodeAdded):
    be(newStewardCli)
    nodeIp, nodePort = genHa()
    clientIp, clientPort = genHa()
    vals['newNodeData'][NODE_IP] = nodeIp
    vals['newNodeData'][NODE_PORT] = nodePort
    vals['newNodeData'][CLIENT_IP] = nodeIp
    vals['newNodeData'][CLIENT_PORT] = clientPort
    doNodeCmd(do, nodeData=vals)
    exitFromCli(do)


def testConsecutiveAddSameNodeWithOnlyAliasChange(be, do,
                                                  newStewardCli, newNodeAdded):
    be(newStewardCli)
    vals['newNodeData'][ALIAS] = randomString(6)
    doNodeCmd(do, nodeData=vals,
              expMsgs=['existing data has conflicts with request data'])
    exitFromCli(do)
