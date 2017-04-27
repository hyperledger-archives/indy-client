import pytest
from plenum.common.signer_simple import SimpleSigner
from sovrin_client.client.wallet.wallet import Wallet
from sovrin_client.test.cli.helper import prompt_is
from sovrin_common.roles import Roles
from sovrin_node.test.did.conftest import wallet, abbrevVerkey, abbrevIdr


@pytest.fixture("module")
def trustAnchorSigner():
    return SimpleSigner()


@pytest.fixture("module")
def trustAnchorWallet(trustAnchorSigner):
    w = Wallet(trustAnchorSigner.identifier)
    w.addIdentifier(signer=trustAnchorSigner)
    return w


def testPoolNodesStarted(poolNodesStarted):
    pass


@pytest.fixture(scope="module")
def philCli(be, do, poolNodesStarted, philCLI, connectedToTest):
    be(philCLI)
    do('prompt Phil', expect=prompt_is('Phil'))

    do('new keyring Phil', expect=['New keyring Phil created',
                                   'Active keyring set to "Phil"'])

    mapper = {
        'seed': '11111111111111111111111111111111',
        'idr': '5rArie7XKukPCaEwq5XGQJnM9Fc5aZE3M9HAPVfMU2xC'}
    do('new key with seed {seed}', expect=['Key created in keyring Phil',
                                           'Identifier for key is {idr}',
                                           'Current identifier set to {idr}'],
       mapper=mapper)

    do('connect test', within=3, expect=connectedToTest)
    return philCLI


@pytest.fixture(scope="module")
def aliceCli(be, do, poolNodesStarted, aliceCLI, connectedToTest, wallet):
    be(aliceCLI)
    do('prompt Alice', expect=prompt_is('Alice'))
    addAndActivateCLIWallet(aliceCLI, wallet)
    do('connect test', within=3, expect=connectedToTest)
    return aliceCLI


@pytest.fixture(scope="module")
def trustAnchorCli(be, do, poolNodesStarted, earlCLI, connectedToTest,
               trustAnchorWallet):
    be(earlCLI)
    do('prompt Earl', expect=prompt_is('Earl'))
    addAndActivateCLIWallet(earlCLI, trustAnchorWallet)
    do('connect test', within=3, expect=connectedToTest)
    return earlCLI


def getNym(be, do, userCli, idr, expectedMsgs):
    be(userCli)
    do('send GET_NYM dest={}'.format(idr),
       within=3,
       expect=expectedMsgs
       )


def getNymNotFoundExpectedMsgs(idr):
    return ["NYM {} not found".format(idr)]


def testGetDIDWithoutAddingIt(be, do, philCli, abbrevIdr):
    getNym(be, do, philCli, abbrevIdr,
           getNymNotFoundExpectedMsgs(abbrevIdr))


def testGetCIDWithoutAddingIt(be, do, philCli, trustAnchorSigner):
    getNym(be, do, philCli, trustAnchorSigner.identifier,
           getNymNotFoundExpectedMsgs(trustAnchorSigner.identifier))


def addNym(be, do, userCli, idr, verkey=None, role=None):
    be(userCli)
    cmd = 'send NYM dest={}'.format(idr)
    if role is not None:
        cmd += ' role={}'.format(role)
    if verkey is not None:
        cmd = '{} verkey={}'.format(cmd, verkey)

    do(cmd, within=5, expect=["Nym {} added".format(idr)])


def addAndActivateCLIWallet(cli, wallet):
    cli.wallets[wallet.name] = wallet
    cli.activeWallet = wallet


@pytest.fixture(scope="module")
def didAdded(be, do, philCli, abbrevIdr):
    addNym(be, do, philCli, abbrevIdr, role=Roles.TRUST_ANCHOR.name)
    return philCli


def testAddDID(didAdded):
    pass


@pytest.fixture(scope="module")
def cidAdded(be, do, philCli, trustAnchorSigner):
    addNym(be, do, philCli, trustAnchorSigner.identifier, role=Roles.TRUST_ANCHOR.name)
    return philCli


def testAddCID(cidAdded):
    pass


def getNoVerkeyEverAssignedMsgs(idr):
    return ["No verkey ever assigned to the identifier {}".format(idr)]


def testGetDIDWithoutVerkey(be, do, philCli, didAdded, abbrevIdr):
    getNym(be, do, philCli, abbrevIdr,
           getNoVerkeyEverAssignedMsgs(abbrevIdr))


def getVerkeyIsSameAsIdentifierMsgs(idr):
    return ["Current verkey is same as identifier {}".format(idr)]


def testGetCIDWithoutVerkey(be, do, philCli, cidAdded, trustAnchorSigner):
    getNym(be, do, philCli, trustAnchorSigner.identifier,
           getVerkeyIsSameAsIdentifierMsgs(trustAnchorSigner.identifier))


@pytest.fixture(scope="module")
def verkeyAddedToDID(be, do, philCli, didAdded, abbrevIdr, abbrevVerkey):
    addNym(be, do, philCli, abbrevIdr, abbrevVerkey)


def testAddVerkeyToExistingDID(verkeyAddedToDID):
    pass


@pytest.fixture(scope="module")
def verkeyAddedToCID(be, do, philCli, cidAdded, trustAnchorWallet):
    newSigner = SimpleSigner()
    addNym(be, do, philCli, trustAnchorWallet.defaultId, newSigner.identifier)
    # Updating the identifier of the new signer to match the one in wallet
    newSigner._identifier = trustAnchorWallet.defaultId
    trustAnchorWallet.updateSigner(trustAnchorWallet.defaultId, newSigner)
    return newSigner


def testAddVerkeyToExistingCID(verkeyAddedToCID):
    pass


def getCurrentVerkeyIsgMsgs(idr, verkey):
    return ["Current verkey for NYM {} is {}".format(idr, verkey)]


def testGetDIDWithVerKey(be, do, philCli, verkeyAddedToDID,
                            abbrevIdr, abbrevVerkey):
    getNym(be, do, philCli, abbrevIdr,
           getCurrentVerkeyIsgMsgs(abbrevIdr, abbrevVerkey))


def testGetCIDWithVerKey(be, do, philCli, verkeyAddedToCID,
                            trustAnchorSigner):
    getNym(be, do, philCli, trustAnchorSigner.identifier,
           getCurrentVerkeyIsgMsgs(trustAnchorSigner.identifier,
                                   verkeyAddedToCID.verkey))


def getNoActiveVerkeyFoundMsgs(idr):
    return ["No active verkey found for the identifier {}".format(idr)]


def addAttribToNym(be, do, userCli, idr, raw):
    be(userCli)
    do('send ATTRIB dest={} raw={}'.format(idr, raw),
       within=5,
       expect=["Attribute added for nym {}".format(idr)])


def testSendAttribForDID(be, do, verkeyAddedToDID, abbrevIdr, aliceCli):
    raw = '{"name": "Alice"}'
    addAttribToNym(be, do, aliceCli, abbrevIdr, raw)


def testSendAttribForCID(be, do, verkeyAddedToCID, trustAnchorSigner, trustAnchorCli):
    raw = '{"name": "Earl"}'
    addAttribToNym(be, do, trustAnchorCli, trustAnchorSigner.identifier, raw)


@pytest.fixture(scope="module")
def verkeyRemovedFromExistingDID(be, do, verkeyAddedToDID, abbrevIdr, aliceCli):
    be(aliceCli)
    addNym(be, do, aliceCli, abbrevIdr, '')
    getNym(be, do, aliceCli, abbrevIdr, getNoActiveVerkeyFoundMsgs(abbrevIdr))


def testRemoveVerkeyFromDID(verkeyRemovedFromExistingDID):
    pass


@pytest.fixture(scope="module")
def verkeyRemovedFromExistingCID(be, do, verkeyAddedToCID,
                                 trustAnchorSigner, trustAnchorCli, trustAnchorWallet):
    be(trustAnchorCli)
    addNym(be, do, trustAnchorCli, trustAnchorSigner.identifier, '')
    getNym(be, do, trustAnchorCli, trustAnchorSigner.identifier,
           getNoActiveVerkeyFoundMsgs(trustAnchorSigner.identifier))


def testRemoveVerkeyFromCID(verkeyRemovedFromExistingCID):
    pass


@pytest.mark.skip(reason="SOV-568. Obsolete assumption, if an identity has set "
                         "its verkey to blank, no-one including "
                         "itself can change it")
def testNewverkeyAddedToDID(be, do, philCli, abbrevIdr,
                            verkeyRemovedFromExistingDID):
    newSigner = SimpleSigner()
    addNym(be, do, philCli, abbrevIdr, newSigner.verkey)
    getNym(be, do, philCli, abbrevIdr,
           getCurrentVerkeyIsgMsgs(abbrevIdr, newSigner.verkey))


@pytest.mark.skip(reason="SOV-568. Obsolete assumption, if an identity has set "
                         "its verkey to blank, no-one including "
                         "itself can change it")
def testNewverkeyAddedToCID(be, do, philCli, trustAnchorSigner,
                            verkeyRemovedFromExistingCID):
    newSigner = SimpleSigner()
    addNym(be, do, philCli, trustAnchorSigner.identifier, newSigner.verkey)
    getNym(be, do, philCli, trustAnchorSigner.identifier,
           getCurrentVerkeyIsgMsgs(trustAnchorSigner.identifier, newSigner.verkey))


def testNewKeyChangesWalletsDefaultId(be, do, poolNodesStarted,
                                      susanCLI, connectedToTest):
    mywallet = Wallet('my wallet')
    keyseed = 'a' * 32
    idr, _ = mywallet.addIdentifier(seed=keyseed.encode("utf-8"))

    be(susanCLI)

    do('connect test', within=3, expect=connectedToTest)

    do('new key with seed {}'.format(keyseed))

    do('send NYM dest={}'.format(idr))

    do('new key with seed 11111111111111111111111111111111')

    do('send NYM dest={}'.format(idr), within=3,
       expect=["Nym {} added".format(idr)])




