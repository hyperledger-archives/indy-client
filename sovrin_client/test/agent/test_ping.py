from sovrin_client.test import waits
from stp_core.loop.eventually import eventually

whitelist = ["is not connected - message will not be sent immediately.If this problem does not resolve itself - check your firewall settings"]

def testPing(aliceAcceptedFaber, faberIsRunning, aliceAgent, emptyLooper):
    faberAgent, _ = faberIsRunning
    recvdPings = faberAgent.spylog.count(faberAgent._handlePing.__name__)
    recvdPongs = aliceAgent.spylog.count(aliceAgent._handlePong.__name__)
    aliceAgent.sendPing('Faber College')

    def chk():
        assert (recvdPings + 1) == faberAgent.spylog.count(
            faberAgent._handlePing.__name__)
        assert (recvdPongs + 1) == aliceAgent.spylog.count(
            aliceAgent._handlePong.__name__)

    timeout = waits.expectedAgentPing()
    emptyLooper.run(eventually(chk, retryWait=1, timeout=timeout))


