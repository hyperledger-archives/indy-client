
def checkWalletState(cli, totalIds, isAbbr, isCrypto):

    if cli._activeWallet:
        assert len(cli._activeWallet.idsToSigners) == totalIds

    if totalIds > 0:
        activeSigner = cli._activeWallet.idsToSigners[
            cli._activeWallet.defaultId]

        if isAbbr:
            assert activeSigner.verkey.startswith("~"), \
                "verkey {} doesn't look like abbreviated verkey".\
                    format(activeSigner.verkey)

            assert cli._activeWallet.defaultId != activeSigner.verkey, \
                "new identifier should not be equal to abbreviated verkey"

        if isCrypto:
            assert not activeSigner.verkey.startswith("~"), \
                "verkey {} doesn't look like cryptographic verkey". \
                    format(activeSigner.verkey)

            assert cli._activeWallet.defaultId == activeSigner.verkey, \
                "new identifier should be equal to verkey"


def getTotalIds(cli):
    if cli._activeWallet:
        return len(cli._activeWallet.idsToSigners)
    else:
        return 0


def testNewIdWithIncorrectSeed(be, do, aliceCLI):
    totalIds = getTotalIds(aliceCLI)
    be(aliceCLI)
    do("new identifier with seed aaaaaaaaaaa",
       expect=["Seed needs to be 32 characters long"])
    checkWalletState(aliceCLI, totalIds=totalIds+0, isAbbr=False, isCrypto=False)


def testNewIdIsNotInvalidCommand(be, do, aliceCLI):
    totalIds = getTotalIds(aliceCLI)
    be(aliceCLI)
    do("new identifier", not_expect=["Invalid command"])
    checkWalletState(aliceCLI, totalIds=totalIds+1, isAbbr=False, isCrypto=False)


def testNewId(be, do, aliceCLI):
    totalIds = getTotalIds(aliceCLI)
    be(aliceCLI)
    do("new identifier",
       expect=["Current identifier set to"])
    checkWalletState(aliceCLI, totalIds=totalIds+1, isAbbr=False, isCrypto=False)


def testNewIdAbbr(be, do, aliceCLI):
    totalIds = getTotalIds(aliceCLI)
    be(aliceCLI)
    do("new identifier abbr",
       expect=["Current identifier set to"])
    checkWalletState(aliceCLI, totalIds=totalIds+1, isAbbr=True, isCrypto=False)


def testNewIdCrypto(be, do, aliceCLI):
    totalIds = getTotalIds(aliceCLI)
    be(aliceCLI)
    do("new identifier crypto",
       expect=["Current identifier set to"])
    checkWalletState(aliceCLI, totalIds=totalIds+1, isAbbr=False, isCrypto=True)


def testNewIdWithAlias(be, do, aliceCLI):
    totalIds = getTotalIds(aliceCLI)
    be(aliceCLI)
    do("new identifier crypto",
       expect=["Current identifier set to"])
    do("new identifier crypto",
       expect=["Current identifier set to"])
    checkWalletState(aliceCLI, totalIds=totalIds + 2, isAbbr=False,
                     isCrypto=True)


