import os

from stp_core.crypto.util import ed25519PkToCurve25519
from plenum.common.util import friendlyToRaw, rawToFriendly

from plenum.common.signer_simple import SimpleSigner
# from sovrin_client.agent.agent import runAgent
# from sovrin_client.agent.agent import runBootstrap

from sovrin_client.client.wallet.wallet import Wallet
from sovrin_common.config_util import getConfig

def processInvAccept(wallet, msg):
    pass

def friendlyVerkeyToPubkey(verkey):
    vkRaw = friendlyToRaw(verkey)
    pkraw = ed25519PkToCurve25519(vkRaw)
    return rawToFriendly(pkraw)

def getClaimVersionFileName(agentName):
    return agentName.replace(" ", "-").lower() + "-schema-version.txt"


def updateAndGetNextClaimVersionNumber(basedirpath, fileName):
    claimVersionFilePath = '{}/{}'.format(basedirpath, fileName)
    # get version number from file
    claimVersionNumber = 0.01
    if os.path.isfile(claimVersionFilePath):
        with open(claimVersionFilePath, mode='r+') as file:
            claimVersionNumber = float(file.read()) + 0.001
            file.seek(0)
            # increment version and update file
            file.write(str(claimVersionNumber))
            file.truncate()
    else:
        with open(claimVersionFilePath, mode='w') as file:
            file.write(str(claimVersionNumber))
    return claimVersionNumber


def build_wallet_core(wallet_name, seed_file):
    config = getConfig()
    baseDir = os.path.expanduser(config.baseDir)

    seedFilePath = '{}/{}'.format(baseDir, seed_file)
    seed = wallet_name + '0'*(32 - len(wallet_name))

    # if seed file is available, read seed from it
    if os.path.isfile(seedFilePath):
        with open(seedFilePath, mode='r+') as file:
            seed = file.read().strip(' \t\n\r')
    wallet = Wallet(wallet_name)

    seed = bytes(seed, encoding='utf-8')
    wallet.addIdentifier(signer=SimpleSigner(seed=seed))

    return wallet


def run_agent(looper, wallet, agent):

    def run():
        _agent = agent
        wallet.pendSyncRequests()
        prepared = wallet.preparePending()
        _agent.client.submitReqs(*prepared)

        runAgent(_agent, looper)

        return _agent, wallet

    return run
