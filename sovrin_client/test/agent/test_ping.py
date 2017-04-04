from stp_core.loop.eventually import eventually
from plenum.test.testable import spy, SpyLog

from sovrin_client.agent.constants import PING, PONG

def testPing(aliceAcceptedFaber, faberIsRunning, aliceAgent, emptyLooper):
    faberAgent, _ = faberIsRunning

    faber_log = SpyLog()
    alice_log = SpyLog()
    faberAgent.msgHandlers[PING] = spy(faberAgent._handlePing, False, True, spy_log=faber_log)
    aliceAgent.msgHandlers[PONG] = spy(aliceAgent._handlePong, False, True, spy_log=alice_log)

    recvd_pings = 0
    recvd_pongs = 0
    aliceAgent.sendPing('Faber College')

    def chk():
        assert (recvd_pings + 1) == faber_log.count(
            faberAgent._handlePing.__name__)
        assert (recvd_pongs + 1) == alice_log.count(
            aliceAgent._handlePong.__name__)

    emptyLooper.run(eventually(chk, retryWait=1, timeout=5))


