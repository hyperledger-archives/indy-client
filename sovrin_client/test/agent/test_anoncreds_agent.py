from plenum.common.eventually import eventually

from anoncreds.protocol.types import SchemaKey, ID


def testAnonCreds(aliceAgent, aliceAcceptedFaber, aliceAcceptedAcme,
                  acmeAgent, emptyLooper):
    # 1. request Claims from Faber
    faberLink = aliceAgent.wallet.getLink('Faber College')
    name, version, origin = faberLink.availableClaims[0]
    schemaKey = SchemaKey(name, version, origin)
    aliceAgent.sendReqClaim(faberLink, schemaKey)

    # 2. check that claim is received from Faber
    async def chkClaims():
        claim = await aliceAgent.prover.wallet.getClaims(ID(schemaKey))
        assert claim.primaryClaim

    emptyLooper.run(eventually(chkClaims, timeout=20))

    # 3. send claim proof to Acme
    acmeLink, acmeClaimPrfReq = aliceAgent.wallet.getMatchingLinksWithClaimReq("Job-Application", "Acme Corp")[0]
    aliceAgent.sendProof(acmeLink, acmeClaimPrfReq)

    # 4. check that claim proof is verified by Acme
    def chkProof():
        internalId = acmeAgent.getInternalIdByInvitedNonce(acmeLink.invitationNonce)
        link = acmeAgent.wallet.getLinkByInternalId(internalId)
        assert "Job-Application" in link.verifiedClaimProofs

    emptyLooper.run(eventually(chkProof, timeout=20))
