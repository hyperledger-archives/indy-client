import pytest
from stp_core.crypto.util import randomSeed

from plenum.common.constants import NODE_IP, NODE_PORT, CLIENT_IP, CLIENT_PORT, \
    ALIAS, SERVICES, VALIDATOR
from plenum.common.signer_simple import SimpleSigner
from plenum.common.util import cryptonymToHex, randomString
from sovrin_client.test.cli.conftest import newStewardCli as getNewStewardCli, \
    newStewardVals as getNewStewardVals, newNodeVals as getNewNodeVals
from sovrin_client.test.cli.helper import addAgent

CONNECTED_TO_TEST = "Connected to test"
NYM_ADDED_OUT = "Nym {remote} added"
NODE_REQUEST_COMPLETED = "Node request completed"
NODE_REQUEST_FAILED = "Node request failed"
INVALID_SYNTAX = "Invalid syntax"


@pytest.yield_fixture(scope="function")
def cliWithRandomName(CliBuilder):
    yield from CliBuilder(randomString(6))


@pytest.fixture(scope="function")
def newStewardVals():
    return getNewStewardVals()


@pytest.fixture(scope="function")
def newNodeVals():
    return getNewNodeVals()


@pytest.fixture(scope="function")
def newStewardCli(be, do, poolNodesStarted, trusteeCli,
                  cliWithRandomName, newStewardVals):
    return getNewStewardCli(be, do, poolNodesStarted, trusteeCli,
                            CONNECTED_TO_TEST, NYM_ADDED_OUT,
                            cliWithRandomName, newStewardVals)


def ensurePoolIsOperable(be, do, cli):
    randomNymMapper = {
        'remote': SimpleSigner(seed=randomSeed()).identifier
    }
    addAgent(be, do, cli, randomNymMapper, CONNECTED_TO_TEST, NYM_ADDED_OUT)


def testSendNodeSucceedsIfServicesIsArrayWithValidatorValueOnly(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    newNodeVals['newNodeData'][SERVICES] = [VALIDATOR]

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=NODE_REQUEST_COMPLETED, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


def testSendNodeSucceedsIfServicesIsEmptyArray(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    newNodeVals['newNodeData'][SERVICES] = []

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=NODE_REQUEST_COMPLETED, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


@pytest.mark.skip(reason='SOV-1092')
def testSendNodeFailsIfDestIsSmallDecimalNumber(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    newNodeVals['newNodeIdr'] = 42

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=NODE_REQUEST_FAILED, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


@pytest.mark.skip(reason='SOV-1092')
def testSendNodeFailsIfDestIsShortReadableName(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    newNodeVals['newNodeIdr'] = 'TheNewNode'

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=NODE_REQUEST_FAILED, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


def testSendNodeFailsIfDestIsHexKey(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    newNodeVals['newNodeIdr'] = cryptonymToHex(
        newNodeVals['newNodeIdr']).decode()

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=NODE_REQUEST_FAILED, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


@pytest.mark.skip(reason='SOV-1096')
def testSendNodeHasInvalidSyntaxIfDestIsEmpty(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    newNodeVals['newNodeIdr'] = ''

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=INVALID_SYNTAX, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


@pytest.mark.skip(reason='SOV-1096')
def testSendNodeHasInvalidSyntaxIfDestIsMissed(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    be(newStewardCli)
    do('send NODE data={newNodeData}',
       mapper=newNodeVals, expect=INVALID_SYNTAX, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


def testSendNodeFailsIfNodeIpContainsLeadingSpace(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    newNodeVals['newNodeData'][NODE_IP] = ' 122.62.52.13'

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=NODE_REQUEST_FAILED, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


def testSendNodeFailsIfNodeIpContainsTrailingSpace(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    newNodeVals['newNodeData'][NODE_IP] = '122.62.52.13 '

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=NODE_REQUEST_FAILED, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


def testSendNodeFailsIfNodeIpHasWrongFormat(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    newNodeVals['newNodeData'][NODE_IP] = '122.62.52'

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=NODE_REQUEST_FAILED, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


def testSendNodeFailsIfNodeIpComponentsAreOutOfBounds(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    newNodeVals['newNodeData'][NODE_IP] = '88.155.256.248'

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=NODE_REQUEST_FAILED, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


def testSendNodeFailsIfNodeIpComponentsAreZeroes(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    newNodeVals['newNodeData'][NODE_IP] = '0.0.0.0'

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=NODE_REQUEST_FAILED, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


def testSendNodeFailsIfNodeIpIsEmpty(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    newNodeVals['newNodeData'][NODE_IP] = ''

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=NODE_REQUEST_FAILED, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


def testSendNodeFailsIfNodeIpIsMissed(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    del newNodeVals['newNodeData'][NODE_IP]

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=NODE_REQUEST_FAILED, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


def testSendNodeFailsIfNodePortIsNegative(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    newNodeVals['newNodeData'][NODE_PORT] = -1

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=NODE_REQUEST_FAILED, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


def testSendNodeFailsIfNodePortIsZero(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    newNodeVals['newNodeData'][NODE_PORT] = 0

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=NODE_REQUEST_FAILED, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


def testSendNodeFailsIfNodePortIsHigherThanUpperBound(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    newNodeVals['newNodeData'][NODE_PORT] = 65536

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=NODE_REQUEST_FAILED, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


def testSendNodeFailsIfNodePortIsFloat(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    newNodeVals['newNodeData'][NODE_PORT] = 5555.5

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=NODE_REQUEST_FAILED, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


def testSendNodeFailsIfNodePortHasWrongFormat(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    newNodeVals['newNodeData'][NODE_PORT] = 'ninety'

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=NODE_REQUEST_FAILED, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


def testSendNodeFailsIfNodePortIsEmpty(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    newNodeVals['newNodeData'][NODE_PORT] = ''

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=NODE_REQUEST_FAILED, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


def testSendNodeFailsIfNodePortIsMissed(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    del newNodeVals['newNodeData'][NODE_PORT]

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=NODE_REQUEST_FAILED, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


def testSendNodeFailsIfClientIpContainsLeadingSpace(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    newNodeVals['newNodeData'][CLIENT_IP] = ' 122.62.52.13'

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=NODE_REQUEST_FAILED, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


def testSendNodeFailsIfClientIpContainsTrailingSpace(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    newNodeVals['newNodeData'][CLIENT_IP] = '122.62.52.13 '

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=NODE_REQUEST_FAILED, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


def testSendNodeFailsIfClientIpHasWrongFormat(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    newNodeVals['newNodeData'][CLIENT_IP] = '122.62.52'

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=NODE_REQUEST_FAILED, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


def testSendNodeFailsIfClientIpComponentsAreOutOfBounds(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    newNodeVals['newNodeData'][CLIENT_IP] = '88.155.256.248'

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=NODE_REQUEST_FAILED, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


def testSendNodeFailsIfClientIpComponentsAreZeroes(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    newNodeVals['newNodeData'][CLIENT_IP] = '0.0.0.0'

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=NODE_REQUEST_FAILED, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


def testSendNodeFailsIfClientIpIsEmpty(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    newNodeVals['newNodeData'][CLIENT_IP] = ''

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=NODE_REQUEST_FAILED, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


def testSendNodeFailsIfClientIpIsMissed(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    del newNodeVals['newNodeData'][CLIENT_IP]

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=NODE_REQUEST_FAILED, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


def testSendNodeFailsIfClientPortIsNegative(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    newNodeVals['newNodeData'][CLIENT_PORT] = -1

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=NODE_REQUEST_FAILED, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


def testSendNodeFailsIfClientPortIsZero(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    newNodeVals['newNodeData'][CLIENT_PORT] = 0

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=NODE_REQUEST_FAILED, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


def testSendNodeFailsIfClientPortIsHigherThanUpperBound(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    newNodeVals['newNodeData'][CLIENT_PORT] = 65536

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=NODE_REQUEST_FAILED, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


def testSendNodeFailsIfClientPortIsFloat(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    newNodeVals['newNodeData'][CLIENT_PORT] = 5555.5

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=NODE_REQUEST_FAILED, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


def testSendNodeFailsIfClientPortHasWrongFormat(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    newNodeVals['newNodeData'][CLIENT_PORT] = 'ninety'

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=NODE_REQUEST_FAILED, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


def testSendNodeFailsIfClientPortIsEmpty(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    newNodeVals['newNodeData'][CLIENT_PORT] = ''

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=NODE_REQUEST_FAILED, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


def testSendNodeFailsIfClientPortIsMissed(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    del newNodeVals['newNodeData'][CLIENT_PORT]

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=NODE_REQUEST_FAILED, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


@pytest.mark.skip(reason='SOV-1093')
def testSendNodeFailsIfAliasIsEmpty(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    newNodeVals['newNodeData'][ALIAS] = ''

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=NODE_REQUEST_FAILED, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


def testSendNodeFailsIfAliasIsMissed(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    del newNodeVals['newNodeData'][ALIAS]

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=NODE_REQUEST_FAILED, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


@pytest.mark.skip(reason='SOV-1094')
def testSendNodeFailsIfServicesContainsUnknownValue(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    newNodeVals['newNodeData'][SERVICES] = [VALIDATOR, 'DECIDER']

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=NODE_REQUEST_FAILED, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


@pytest.mark.skip(reason='SOV-1094')
def testSendNodeFailsIfServicesIsValidatorValue(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    newNodeVals['newNodeData'][SERVICES] = VALIDATOR # just string, not array

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=NODE_REQUEST_FAILED, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


@pytest.mark.skip(reason='SOV-1094')
def testSendNodeFailsIfServicesIsEmptyString(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    newNodeVals['newNodeData'][SERVICES] = ''

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=NODE_REQUEST_FAILED, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


@pytest.mark.skip(reason='SOV-1091')
def testSendNodeFailsIfServicesIsMissed(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    del newNodeVals['newNodeData'][SERVICES]

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=NODE_REQUEST_FAILED, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


@pytest.mark.skip(reason='SOV-1095')
def testSendNodeFailsIfDataContainsUnknownField(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    newNodeVals['newNodeData']['extra'] = 42

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=NODE_REQUEST_FAILED, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


def testSendNodeFailsIfDataIsEmptyJson(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    newNodeVals['newNodeData'] = {}

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=NODE_REQUEST_FAILED, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


@pytest.mark.skip(reason='SOV-1096')
def testSendNodeHasInvalidSyntaxIfDataIsBrokenJson(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    newNodeVals['newNodeData'] = "{'node_ip': '10.0.0.105', 'node_port': 9701"

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=INVALID_SYNTAX, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


@pytest.mark.skip(reason='SOV-1096')
def testSendNodeHasInvalidSyntaxIfDataIsNotJson(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    newNodeVals['newNodeData'] = 'not_json'

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=INVALID_SYNTAX, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


@pytest.mark.skip(reason='SOV-1096')
def testSendNodeHasInvalidSyntaxIfDataIsEmptyString(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    newNodeVals['newNodeData'] = ''

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       mapper=newNodeVals, expect=INVALID_SYNTAX, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


@pytest.mark.skip(reason='SOV-1096')
def testSendNodeHasInvalidSyntaxIfDataIsMissed(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    be(newStewardCli)
    do('send NODE dest={newNodeIdr}',
       mapper=newNodeVals, expect=INVALID_SYNTAX, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


@pytest.mark.skip(reason='SOV-1096')
def testSendNodeHasInvalidSyntaxIfUnknownParameterIsPassed(
        be, do, poolNodesStarted, newStewardCli, newNodeVals):

    be(newStewardCli)
    do('send NODE dest={newNodeIdr} data={newNodeData} extra=42',
       mapper=newNodeVals, expect=INVALID_SYNTAX, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)


def testSendNodeHasInvalidSyntaxIfAllParametersAreMissed(
        be, do, poolNodesStarted, newStewardCli):

    be(newStewardCli)
    do('send NODE', expect=INVALID_SYNTAX, within=8)

    ensurePoolIsOperable(be, do, newStewardCli)
