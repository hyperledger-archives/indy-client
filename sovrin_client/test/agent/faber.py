from plenum.common.log import getlogger

from anoncreds.protocol.types import AttribType, AttribDef, SchemaKey
from sovrin_client.agent.agent import createAgent
from sovrin_client.client.client import Client
from sovrin_client.client.wallet.wallet import Wallet
from sovrin_client.test.agent.base_agent import BaseAgent
from sovrin_client.test.agent.helper import buildFaberWallet
from sovrin_client.test.agent.test_walleted_agent import TestWalletedAgent
from sovrin_client.test.helper import TestClient

logger = getlogger()


class FaberAgent(BaseAgent):
    def __init__(self,
                 basedirpath: str,
                 client: Client = None,
                 wallet: Wallet = None,
                 port: int = None,
                 loop=None):

        portParam, = self.getPassedArgs()

        super().__init__('Faber College', basedirpath, client, wallet,
                         portParam or port, loop=loop)

        # maps invitation nonces to internal ids
        self._invites = {
            "b1134a647eb818069c089e7694f63e6d": 1,
            "2a2eb72eca8b404e8d412c5bf79f2640": 2,
            "7513d1397e87cada4214e2a650f603eb": 3,
            "710b78be79f29fc81335abaa4ee1c5e8": 4
        }

        self._attrDef = AttribDef('Transcript',
                                  [AttribType('student_name', encode=True),
                                   AttribType('ssn', encode=True),
                                   AttribType('degree', encode=True),
                                   AttribType('year', encode=True),
                                   AttribType('status', encode=True)])

        # maps internal ids to attributes
        self._attrs = {
            1: self._attrDef.attribs(
                student_name="Alice Garcia",
                ssn="123-45-6789",
                degree="Bachelor of Science, Marketing",
                year="2015",
                status="graduated"),
            2: self._attrDef.attribs(
                student_name="Carol Atkinson",
                ssn="783-41-2695",
                degree="Bachelor of Science, Physics",
                year="2012",
                status="graduated"),
            3: self._attrDef.attribs(
                student_name="Frank Jeffrey",
                ssn="996-54-1211",
                degree="Bachelor of Arts, History",
                year="2013",
                status="dropped"),
            4: self._attrDef.attribs(
                student_name="Craig Richards",
                ssn="151-44-5876",
                degree="MBA, Finance",
                year="2015",
                status="graduated")
        }


    def getAttrDefs(self):
        return [self._attrDef]

    def getAttrs(self):
        return self._attrs

    def getSchemaKeysToBeGenerated(self):
        return [SchemaKey("Transcript", "1.2", self.wallet.defaultId)]


def createFaber(name=None, wallet=None, basedirpath=None, port=None):
    return createAgent(FaberAgent, name or "Faber College",
                       wallet or buildFaberWallet(),
                       basedirpath, port, clientClass=TestClient)


if __name__ == "__main__":
    TestWalletedAgent.createAndRunAgent(
        FaberAgent, "Faber College", wallet=buildFaberWallet(),
        basedirpath=None, port=5555, looper=None, clientClass=TestClient)
