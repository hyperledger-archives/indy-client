import json
import logging
import re

import pytest
from plenum.common.constants import PUBKEY

from anoncreds.protocol.types import SchemaKey, ID
from sovrin_client.test import waits
from sovrin_common.roles import Roles
from stp_core.loop.eventually import eventually
from sovrin_client.test.agent.test_walleted_agent import TestWalletedAgent
from sovrin_common.setup_util import Setup
from sovrin_common.constants import ENDPOINT

from sovrin_client.test.agent.acme import AcmeAgent
from sovrin_client.test.agent.faber import FaberAgent
from sovrin_client.test.agent.helper import buildFaberWallet, buildAcmeWallet, \
    buildThriftWallet
from sovrin_client.test.agent.thrift import ThriftAgent
from sovrin_client.test.cli.conftest import faberMap, acmeMap, \
    thriftMap
from sovrin_client.test.cli.helper import newCLI
from sovrin_client.test.cli.test_tutorial import syncInvite, acceptInvitation, \
    aliceRequestedTranscriptClaim, jobApplicationProofSent, \
    jobCertClaimRequested, bankBasicProofSent, bankKYCProofSent, \
    setPromptAndKeyring
from sovrin_client.test.helper import TestClient

concerningLogLevels = [logging.WARNING,
                       logging.ERROR,
                       logging.CRITICAL]

whitelist = ["is not connected - message will not be sent immediately.If this problem does not resolve itself - check your firewall settings"]

def getSeqNoFromCliOutput(cli):
    seqPat = re.compile("Sequence number is ([0-9]+)")
    m = seqPat.search(cli.lastCmdOutput)
    assert m
    seqNo, = m.groups()
    return seqNo


@pytest.fixture(scope="module")
def newGuyCLI(looper, tdir, tconf):
    Setup(tdir).setupAll()
    return newCLI(looper, tdir, subDirectory='newguy', conf=tconf)


@pytest.mark.skip("SOV-569. Not yet implemented")
def testGettingStartedTutorialAgainstSandbox(newGuyCLI, be, do):
    be(newGuyCLI)
    do('connect test', within=3, expect="Connected to test")
    # TODO finish the entire set of steps


@pytest.mark.skipif('sys.platform == "win32"', reason='SOV-384')
def testManual(do, be, poolNodesStarted, poolTxnStewardData, philCLI,
               connectedToTest, nymAddedOut, attrAddedOut,
               schemaAdded, claimDefAdded, aliceCLI, newKeyringOut, aliceMap,
               tdir, syncLinkOutWithEndpoint, jobCertificateClaimMap,
               syncedInviteAcceptedOutWithoutClaims, transcriptClaimMap,
               reqClaimOut, reqClaimOut1, susanCLI, susanMap):
    eventually.slowFactor = 3

    # Create steward and add nyms and endpoint attributes of all agents
    _, stewardSeed = poolTxnStewardData
    be(philCLI)
    do('new keyring Steward', expect=['New keyring Steward created',
                                      'Active keyring set to "Steward"'])

    mapper = {'seed': stewardSeed.decode()}
    do('new key with seed {seed}', expect=['Key created in keyring Steward'],
       mapper=mapper)
    do('connect test', within=3, expect=connectedToTest)

    # Add nym and endpoint for Faber, Acme and Thrift
    agentIpAddress = "127.0.0.1"
    faberAgentPort = 5555
    acmeAgentPort = 6666
    thriftAgentPort = 7777

    faberHa = "{}:{}".format(agentIpAddress, faberAgentPort)
    acmeHa = "{}:{}".format(agentIpAddress, acmeAgentPort)
    thriftHa = "{}:{}".format(agentIpAddress, thriftAgentPort)
    faberId = 'FuN98eH2eZybECWkofW6A9BKJxxnTatBCopfUiNxo6ZB'
    acmeId = '7YD5NKn3P4wVJLesAmA1rr7sLPqW9mR1nhFdKD518k21'
    thriftId = '9jegUr9vAMqoqQQUEAiCBYNQDnUbTktQY9nNspxfasZW'
    faberPk = '5hmMA64DDQz5NzGJNVtRzNwpkZxktNQds21q3Wxxa62z'
    acmePk = 'C5eqjU7NMVMGGfGfx2ubvX5H9X346bQt5qeziVAo3naQ'
    thriftPk = 'AGBjYvyM3SFnoiDGAEzkSLHvqyzVkXeMZfKDvdpEsC2x'
    for nym, ha, pk in [(faberId, faberHa, faberPk),
                    (acmeId, acmeHa, acmePk),
                    (thriftId, thriftHa, thriftPk)]:
        m = {'target': nym, 'endpoint': json.dumps({ENDPOINT:
                                                    {'ha': ha, PUBKEY: pk}})}
        do('send NYM dest={{target}} role={role}'.format(role=Roles.TRUST_ANCHOR.name),
            within=5,
            expect=nymAddedOut, mapper=m)
        do('send ATTRIB dest={target} raw={endpoint}', within=5,
           expect=attrAddedOut, mapper=m)

    # Start Faber Agent and Acme Agent
    fMap = faberMap(agentIpAddress, faberAgentPort)
    aMap = acmeMap(agentIpAddress, acmeAgentPort)
    tMap = thriftMap(agentIpAddress, thriftAgentPort)

    agentParams = [
        (FaberAgent, "Faber College", faberAgentPort,
         buildFaberWallet),
        (AcmeAgent, "Acme Corp", acmeAgentPort,
         buildAcmeWallet),
        (ThriftAgent, "Thrift Bank", thriftAgentPort,
         buildThriftWallet)
    ]

    faberAgent, acmeAgent, thriftAgent = None, None, None

    def startAgents():
        for agentCls, agentName, agentPort, buildAgentWalletFunc in \
                agentParams:
            agentCls.getPassedArgs = lambda _: (agentPort, False)
            TestWalletedAgent.createAndRunAgent(
                agentName, agentCls, buildAgentWalletFunc(), tdir, agentPort,
                philCLI.looper, TestClient)
        _faberAgent, _acmeAgent, _thriftAgent = None, None, None
        for p in philCLI.looper.prodables:
            if p.name == 'Faber College':
                _faberAgent = p
            if p.name == 'Acme Corp':
                _acmeAgent = p
            if p.name == 'Thrift Bank':
                _thriftAgent = p
        philCLI.looper.runFor(5)
        return _faberAgent, _acmeAgent, _thriftAgent

    def restartAgents():
        for agent in [faberAgent, acmeAgent, thriftAgent]:
            agent.stop()
            philCLI.looper.removeProdable(name=agent.name)
        return startAgents()

    faberAgent, acmeAgent, thriftAgent = startAgents()

    async def checkTranscriptWritten():
        faberId = faberAgent.wallet.defaultId
        schemaId = ID(SchemaKey("Transcript", "1.2", faberId))
        schema = await faberAgent.issuer.wallet.getSchema(schemaId)
        assert schema
        assert schema.seqId

        issuerPublicKey = faberAgent.issuer.wallet.getPublicKey(schemaId)
        assert issuerPublicKey  # TODO isinstance(issuerPublicKey, PublicKey)

    async def checkJobCertWritten():
        acmeId = acmeAgent.wallet.defaultId
        schemaId = ID(SchemaKey("Job-Certificate", "0.2", acmeId))
        schema = await acmeAgent.issuer.wallet.getSchema(schemaId)
        assert schema
        assert schema.seqId

        issuerPublicKey = await acmeAgent.issuer.wallet.getPublicKey(schemaId)
        assert issuerPublicKey
        assert issuerPublicKey.seqId

    timeout = waits.expectedTranscriptWritten()
    philCLI.looper.run(eventually(checkTranscriptWritten, timeout=timeout))
    timeout = waits.expectedJobCertWritten()
    philCLI.looper.run(eventually(checkJobCertWritten, timeout=timeout))

    # Defining inner method for closures
    def executeGstFlow(name, userCLI, userMap, be, connectedToTest, do, fMap,
                       aMap, jobCertificateClaimMap, newKeyringOut, reqClaimOut,
                       reqClaimOut1, syncLinkOutWithEndpoint,
                       syncedInviteAcceptedOutWithoutClaims, tMap,
                       transcriptClaimMap):

        async def getPublicKey(wallet, schemaId):
            return await wallet.getPublicKey(schemaId)

        async def getClaim(schemaId):
            return await userCLI.agent.prover.wallet.getClaims(schemaId)

        # Start User cli

        be(userCLI)
        setPromptAndKeyring(do, name, newKeyringOut, userMap)
        do('connect test', within=3, expect=connectedToTest)
        # Accept faber
        do('load sample/faber-invitation.sovrin')
        syncInvite(be, do, userCLI, syncLinkOutWithEndpoint, fMap)
        do('show link faber')
        acceptInvitation(be, do, userCLI, fMap,
                         syncedInviteAcceptedOutWithoutClaims)

        # TODO: restart agents to test everything still works fine
        # faberAgent, acmeAgent, thriftAgent = restartAgents()

        # Request claim
        do('show claim Transcript')
        aliceRequestedTranscriptClaim(be, do, userCLI, transcriptClaimMap,
                                      reqClaimOut,
                                      None,  # Passing None since its not used
                                      None)  # Passing None since its not used

        faberSchemaId = ID(SchemaKey('Transcript', '1.2', fMap['target']))
        faberIssuerPublicKey = userCLI.looper.run(
            getPublicKey(faberAgent.issuer.wallet, faberSchemaId))
        userFaberIssuerPublicKey = userCLI.looper.run(
            getPublicKey(userCLI.agent.prover.wallet, faberSchemaId))
        assert faberIssuerPublicKey == userFaberIssuerPublicKey

        do('show claim Transcript')
        assert userCLI.looper.run(getClaim(faberSchemaId))

        # Accept acme
        do('load sample/acme-job-application.sovrin')
        syncInvite(be, do, userCLI, syncLinkOutWithEndpoint, aMap)
        acceptInvitation(be, do, userCLI, aMap,
                         syncedInviteAcceptedOutWithoutClaims)
        # Send claim
        do('show claim request Job-Application')
        do('set first_name to Alice')
        do('set last_name to Garcia')
        do('set phone_number to 123-45-6789')
        do('show claim request Job-Application')
        # Passing some args as None since they are not used in the method
        jobApplicationProofSent(be, do, userCLI, aMap, None, None, None)

        # TODO: restart agents to test everything still works fine
        # faberAgent, acmeAgent, thriftAgent = restartAgents()

        do('show claim Job-Certificate')
        # Request new available claims Job-Certificate
        jobCertClaimRequested(be, do, userCLI, None,
                              jobCertificateClaimMap, reqClaimOut1, None)

        acmeSchemaId = ID(SchemaKey('Job-Certificate', '0.2', aMap['target']))
        acmeIssuerPublicKey = userCLI.looper.run(getPublicKey(
            acmeAgent.issuer.wallet, acmeSchemaId))
        userAcmeIssuerPublicKey = userCLI.looper.run(getPublicKey(
            userCLI.agent.prover.wallet, acmeSchemaId))
        assert acmeIssuerPublicKey == userAcmeIssuerPublicKey

        do('show claim Job-Certificate')
        assert userCLI.looper.run(getClaim(acmeSchemaId))

        # Accept thrift
        do('load sample/thrift-loan-application.sovrin')
        acceptInvitation(be, do, userCLI, tMap,
                         syncedInviteAcceptedOutWithoutClaims)

        # TODO: restart agents to test everything still works fine
        # faberAgent, acmeAgent, thriftAgent = restartAgents()

        # Send proofs
        bankBasicProofSent(be, do, userCLI, tMap, None)

        thriftAcmeIssuerPublicKey = userCLI.looper.run(getPublicKey(
            thriftAgent.issuer.wallet, acmeSchemaId))
        assert acmeIssuerPublicKey == thriftAcmeIssuerPublicKey
        passed = False
        try:
            bankKYCProofSent(be, do, userCLI, tMap, None)
            passed = True
        except:
            thriftFaberIssuerPublicKey = userCLI.looper.run(getPublicKey(
                thriftAgent.issuer.wallet, faberSchemaId))
            assert faberIssuerPublicKey == thriftFaberIssuerPublicKey
        assert passed

    executeGstFlow("Alice", aliceCLI, aliceMap, be, connectedToTest, do, fMap,
                   aMap, jobCertificateClaimMap, newKeyringOut, reqClaimOut,
                   reqClaimOut1, syncLinkOutWithEndpoint,
                   syncedInviteAcceptedOutWithoutClaims, tMap,
                   transcriptClaimMap)

    # TODO: restart agents to test everything still works fine
    # faberAgent, acmeAgent, thriftAgent = restartAgents()

    executeGstFlow("Susan", susanCLI, susanMap, be, connectedToTest, do, fMap,
                   aMap, jobCertificateClaimMap, newKeyringOut, reqClaimOut,
                   reqClaimOut1, syncLinkOutWithEndpoint,
                   syncedInviteAcceptedOutWithoutClaims, tMap,
                   transcriptClaimMap)
