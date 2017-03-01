from plenum.common.log import getlogger
from plenum.common.types import f
from plenum.test.testable import Spyable

from sovrin_client.agent.agent import WalletedAgent
from sovrin_common.exceptions import LinkNotFound
from sovrin_common.txn import NONCE
from sovrin_client.test.agent.helper import getAgentCmdLineParams

logger = getlogger()


@Spyable(
    methods=[WalletedAgent._handlePing, WalletedAgent._handlePong])
class TestWalletedAgent(WalletedAgent):
    def getLinkForMsg(self, msg):
        nonce = msg.get(NONCE)
        identifier = msg.get(f.IDENTIFIER.nm)
        link = None
        for _, li in self.wallet._links.items():
            if li.invitationNonce == nonce and li.remoteIdentifier == identifier:
                link = li
                break
        if link:
            return link
        else:
            raise LinkNotFound

    @staticmethod
    def getPassedArgs():
        return getAgentCmdLineParams()

    @staticmethod
    def getEndpointArgs(wallet):
        endpointSeed = wallet._signerById(wallet.defaultId).seed if wallet \
            else None
        onlyListener = True
        return {'seed': endpointSeed,
                'onlyListener': onlyListener}