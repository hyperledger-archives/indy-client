import pyorient
from plenum.persistence.orientdb_store import OrientDbStore
from plenum.test.test_stack import StackedTester, TestStack
from plenum.test.testable import spyable
from sovrin_client.client.client import Client

from sovrin_common.test.helper import TempStorage

from sovrin_common.config_util import getConfig

from stp_core.common.log import getlogger
logger = getlogger()


class TestClientStorage(TempStorage):
    def __init__(self, name, baseDir):
        self.name = name
        self.baseDir = baseDir

    def cleanupDataLocation(self):
        self.cleanupDirectory(self.dataLocation)
        config = getConfig()
        if config.ReqReplyStore == "orientdb" or config.ClientIdentityGraph:
            try:
                self._getOrientDbStore().client.db_drop(self.name)
                logger.debug("Dropped db {}".format(self.name))
            except Exception as ex:
                logger.debug("Error while dropping db {}: {}".format(self.name,
                                                                     ex))


@spyable(methods=[Client.handleOneNodeMsg])
class TestClient(Client, StackedTester, TestClientStorage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        TestClientStorage.__init__(self, self.name, self.basedirpath)

    @staticmethod
    def stackType():
        return TestStack

    def _getOrientDbStore(self):
        config = getConfig()
        return OrientDbStore(user=config.OrientDB["user"],
                             password=config.OrientDB["password"],
                             dbName=self.name,
                             storageType=pyorient.STORAGE_TYPE_MEMORY)

    def onStopping(self, *args, **kwargs):
        # TODO: Why we needed following line?
        # self.cleanupDataLocation()
        super().onStopping(*args, **kwargs)

