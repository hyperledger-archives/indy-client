
def checkWalletState(cli, totalIds):
    if cli._activeWallet:
        assert len(cli._activeWallet.idsToSigners) == totalIds


def testNewIdWithIncorrectSeed(be, do, aliceCLI):
    checkWalletState(aliceCLI, totalIds=0)
    be(aliceCLI)
    do("new identifier with seed aaaaaaaaaaa",
       expect=["Seed needs to be 32 characters long"])
    checkWalletState(aliceCLI, totalIds=0)


def testNewIdIsNotInvalidCommand(be, do, aliceCLI):
    checkWalletState(aliceCLI, totalIds=0)
    be(aliceCLI)
    do("new identifier", not_expect=["Invalid command"])
    checkWalletState(aliceCLI, totalIds=1)


def testNewId(be, do, aliceCLI):
    checkWalletState(aliceCLI, totalIds=1)
    be(aliceCLI)
    do("new identifier",
       expect=["Current identifier set to"])
    checkWalletState(aliceCLI, totalIds=2)
