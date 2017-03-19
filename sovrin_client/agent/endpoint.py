from typing import Callable, Any, List

from plenum.common.log import getlogger
from plenum.common.raet import getHaFromLocalEstate
from plenum.common.stacked import SimpleStack
from plenum.common.types import HA
from plenum.common.util import randomString
from raet.raeting import AutoMode
from raet.road.estating import RemoteEstate

logger = getlogger()


class Endpoint:
    def __init__(self, port: int, msgHandler: Callable,
                 name: str=None, basedirpath: str=None):

        if name and basedirpath:
            ha = getHaFromLocalEstate(name, basedirpath)
            if ha and ha[1] != port:
                port = ha[1]

        self.name = name
        self.stack = None

        self._port = port
        self._msgHandler = msgHandler
        self._basedirpath = basedirpath

    def start(self):
        stackParams = {
            "name": self.name or randomString(8),
            "ha": HA("0.0.0.0", self._port),
            "main": True,
            "auto": AutoMode.always,
            "mutable": "mutable"
        }

        if self._basedirpath:
            stackParams["basedirpath"] = self._basedirpath

        self.stack = SimpleStack(stackParams, self.baseMsgHandler)
        self.stack.start()

    def stop(self):
        if self.stack:
            self.stack.stop()

    def transmitToClient(self, msg: Any, remoteName: str):
        """
        Transmit the specified message to the remote client specified by
         `remoteName`.
        :param msg: a message
        :param remoteName: the name of the remote
        """
        # At this time, nodes are not signing messages to clients, beyond what
        # happens inherently with RAET
        payload = self.stack.prepForSending(msg)
        try:
            self.stack.send(payload, remoteName)
        except Exception as ex:
            logger.error("{} unable to send message {} to client {}; "
                         "Exception: {}".format(self.name, msg, remoteName,
                                               ex.__repr__()))

    def transmitToClients(self, msg: Any, remoteNames: List[str]):
        for nm in remoteNames:
            self.transmitToClient(msg, nm)

    # TODO: Rename method
    def baseMsgHandler(self, msg):
        logger.debug("Got {}".format(msg))
        self._msgHandler(msg)

    def connectTo(self, ha):
        remote = self.stack.findInRemotesByHA(ha)
        if not remote:
            remote = RemoteEstate(stack=self.stack, ha=ha)
            self.stack.addRemote(remote)
            # updates the store time so the join timer is accurate
            self.stack.updateStamp()
            self.stack.join(uid=remote.uid, cascade=True, timeout=30)

    def isConnectedTo(self, name=None, ha=None):
        return self.stack.isConnectedTo(name=name, ha=ha)

    def getRemote(self, name=None, ha=None):
        return self.stack.getRemote(name=name, ha=ha)

    def transmit(self, msg, uid):
        self.stack.transmit(msg, uid)

    async def service(self, limit):
        return await self.stack.service(limit)

