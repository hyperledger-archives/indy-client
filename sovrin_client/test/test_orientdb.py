from plenum.common.log import getlogger

logger = getlogger()


def testAddSteward(nodeSet, stewardWallet, steward):
    for node in nodeSet:
        assert node.graphStore.hasSteward(stewardWallet.defaultId)


def testAddTrustAnchor(nodeSet, addedTrustAnchor):
    for node in nodeSet:
        assert node.graphStore.hasTrustAnchor(addedTrustAnchor.defaultId)
