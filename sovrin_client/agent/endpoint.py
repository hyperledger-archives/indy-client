from typing import Callable, Any, List

from plenum import config
from plenum.common.message_processor import MessageProcessor
from raet.raeting import AutoMode
from zmq.utils import z85

from plenum.common.log import getlogger
from stp_raet.util import getHaFromLocalEstate
from plenum.common.util import randomString, friendlyToRaw
from stp_core.crypto.util import randomSeed
from stp_raet.rstack import SimpleRStack
from stp_core.types import HA
from stp_zmq.zstack import SimpleZStack

logger = getlogger()


class EndpointCore(MessageProcessor):
    # TODO: Rename method
    def baseMsgHandler(self, msg):
        logger.debug("Got {}".format(msg))
        self.msgHandler(msg)

    def transmitToClient(self, msg: Any, remoteName: str):
        """
        Transmit the specified message to the remote client specified by
         `remoteName`.
        :param msg: a message
        :param remoteName: the name of the remote
        """
        # At this time, nodes are not signing messages to clients, beyond what
        # happens inherently with RAET
        payload = self.prepForSending(msg)
        try:
            self.send(payload, remoteName)
        except Exception as ex:
            logger.error("{} unable to send message {} to client {}; "
                         "Exception: {}".format(self.name, msg, remoteName,
                                                ex.__repr__()))

    def transmitToClients(self, msg: Any, remoteNames: List[str]):
        for nm in remoteNames:
            self.transmitToClient(msg, nm)


class REndpoint(SimpleRStack, EndpointCore):
    def __init__(self, port: int, msgHandler: Callable,
                 name: str=None, basedirpath: str=None):
        if name and basedirpath:
            ha = getHaFromLocalEstate(name, basedirpath)
            if ha and ha[1] != port:
                port = ha[1]

        stackParams = {
            "name": name or randomString(8),
            "ha": HA("0.0.0.0", port),
            "main": True,
            "auto": AutoMode.always,
            "mutable": "mutable",
            "messageTimeout": config.RAETMessageTimeout
        }
        if basedirpath:
            stackParams["basedirpath"] = basedirpath

            SimpleRStack.__init__(self, stackParams, self.baseMsgHandler)

        self.msgHandler = msgHandler

    def connectTo(self, ha):
        if not self.isConnectedTo(ha=ha):
            self.connect(ha=ha)
        else:
            logger.debug('{} already connected {}'.format(self, ha))

    def host_address(self) -> str:
        return str(self.ha[0]) + ":" + str(self.ha[1])


class ZEndpoint(SimpleZStack, EndpointCore):
    def __init__(self, port: int, msgHandler: Callable,
                 name: str=None, basedirpath: str=None, seed=None,
                 onlyListener=False):
        stackParams = {
            "name": name or randomString(8),
            "ha": HA("0.0.0.0", port),
            "auto": AutoMode.always
        }
        if basedirpath:
            stackParams["basedirpath"] = basedirpath

        seed = seed or randomSeed()
        SimpleZStack.__init__(self, stackParams, self.baseMsgHandler,
                              seed=seed, onlyListener=onlyListener)

        self.msgHandler = msgHandler

    def connectTo(self, ha, verkey, pubkey):
        if not self.isConnectedTo(ha=ha):
            assert pubkey, 'Need public key to connect to {}'.format(ha)
            zvk = z85.encode(friendlyToRaw(verkey)) if verkey else None
            zpk = z85.encode(friendlyToRaw(pubkey))
            self.connect(name=verkey or pubkey, ha=ha, verKey=zvk, publicKey=zpk)
        else:
            logger.debug('{} already connected {}'.format(self, ha))
