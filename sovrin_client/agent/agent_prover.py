import asyncio
from typing import Any

from plenum.common.txn import NONCE, TYPE, NAME, VERSION, ORIGIN, IDENTIFIER, \
    DATA
from plenum.common.types import f
from plenum.common.util import getCryptonym

from anoncreds.protocol.prover import Prover
from anoncreds.protocol.types import SchemaKey, ID, Claims, ProofInput
from anoncreds.protocol.utils import toDictWithStrValues
from sovrin_client.agent.msg_constants import CLAIM_REQUEST, PROOF, CLAIM_FIELD, \
    CLAIM_REQ_FIELD, PROOF_FIELD, PROOF_INPUT_FIELD, REVEALED_ATTRS_FIELD
from sovrin_client.client.wallet.link import ProofRequest, Link
from sovrin_common.util import getNonceForProof


class AgentProver:
    def __init__(self, prover: Prover):
        self.prover = prover

    def sendReqClaim(self, link: Link, schemaKey):
        if self.loop.is_running():
            self.loop.call_soon(asyncio.ensure_future,
                                self.sendReqClaimAsync(link, schemaKey))
        else:
            self.loop.run_until_complete(
                self.sendReqClaimAsync(link, schemaKey))

    async def sendReqClaimAsync(self, link: Link, schemaKey):
        name, version, origin = schemaKey
        schemaKey = SchemaKey(name, version, origin)

        claimReq = await self.prover.createClaimRequest(
            schemaId=ID(schemaKey),
            proverId=link.invitationNonce,
            reqNonRevoc=False)

        op = {
            NONCE: link.invitationNonce,
            TYPE: CLAIM_REQUEST,
            NAME: name,
            VERSION: version,
            ORIGIN: origin,
            CLAIM_REQ_FIELD: claimReq.toStrDict()
        }

        self.signAndSend(msg=op, linkName=link.name)

    def sendProofReq(self, link: Link, schemaKey):
        if self.loop.is_running():
            self.loop.call_soon(asyncio.ensure_future,
                                self.sendProofReqAsync(link, schemaKey))
        else:
            self.loop.run_until_complete(
                self.sendProofReqAsync(link, schemaKey))

    async def sendProofReqAsync(self, link: Link, schemaKey):
        pass
        name, version, origin = schemaKey
        schemaKey = SchemaKey(name, version, origin)

        claimReq = await self.prover.createClaimRequest(
            schemaId=ID(schemaKey),
            proverId=link.invitationNonce,
            reqNonRevoc=False)

        op = {
            NONCE: link.invitationNonce,
            TYPE: CLAIM_REQUEST,
            NAME: name,
            VERSION: version,
            ORIGIN: origin,
            CLAIM_REQ_FIELD: claimReq.toStrDict()
        }

        self.signAndSend(msg=op, linkName=link.name)

    async def handleReqClaimResponse(self, msg):
        body, _ = msg
        issuerId = body.get(IDENTIFIER)
        claim = body[DATA]
        li = self._getLinkByTarget(getCryptonym(issuerId))
        if li:
            self.notifyResponseFromMsg(li.name, body.get(f.REQ_ID.nm))
            self.notifyMsgListener('    Received claim "{}".\n'.format(
                claim[NAME]))
            name, version, claimAuthor = \
                claim[NAME], claim[VERSION], claim[f.IDENTIFIER.nm]

            schemaKey = SchemaKey(name, version, claimAuthor)
            schema = await self.prover.wallet.getSchema(ID(schemaKey))
            schemaId = ID(schemaKey=schemaKey, schemaId=schema.seqId)

            claim = Claims.fromStrDict(claim[CLAIM_FIELD])

            await self.prover.processClaim(schemaId, claim)
        else:
            self.notifyMsgListener("No matching link found")

    def sendProof(self, link: Link, claimPrfReq: ProofRequest):
        if self.loop.is_running():
            self.loop.call_soon(asyncio.ensure_future,
                                self.sendProofAsync(link, claimPrfReq))
        else:
            self.loop.run_until_complete(self.sendProofAsync(link, claimPrfReq))

    async def sendProofAsync(self, link: Link, claimPrfReq: ProofRequest):
        nonce = getNonceForProof(link.invitationNonce)

        revealedAttrNames = claimPrfReq.verifiableAttributes
        proofInput = ProofInput(revealedAttrs=revealedAttrNames)
        proof, revealedAttrs = await self.prover.presentProof(proofInput, nonce)

        op = {
            NAME: claimPrfReq.name,
            VERSION: claimPrfReq.version,
            NONCE: link.invitationNonce,
            TYPE: PROOF,
            PROOF_FIELD: proof.toStrDict(),
            PROOF_INPUT_FIELD: proofInput.toStrDict(),
            REVEALED_ATTRS_FIELD: toDictWithStrValues(revealedAttrs)
        }

        self.signAndSend(msg=op, linkName=link.name)

    def handleProofStatusResponse(self, msg: Any):
        body, _ = msg
        data = body.get(DATA)
        identifier = body.get(IDENTIFIER)
        li = self._getLinkByTarget(getCryptonym(identifier))
        self.notifyResponseFromMsg(li.name, body.get(f.REQ_ID.nm))
        self.notifyMsgListener(data)

    async def getMatchingLinksWithReceivedClaimAsync(self, claimName=None):
        matchingLinkAndAvailableClaim = self.wallet.getMatchingLinksWithAvailableClaim(
            claimName)
        matchingLinkAndReceivedClaim = []
        for li, cl in matchingLinkAndAvailableClaim:
            name, version, origin = cl
            schemaKeyId = ID(
                SchemaKey(name=name, version=version, issuerId=origin))
            schema = await self.prover.wallet.getSchema(schemaKeyId)
            claimAttrs = set(schema.attrNames)
            claim = None
            try:
                claim = await self.prover.wallet.getClaims(schemaKeyId)
            except ValueError:
                pass  # it means no claim was issued
            attrs = {k: None for k in claimAttrs}
            if claim:
                issuedAttributes = claim.primaryClaim.attrs
                if claimAttrs.intersection(issuedAttributes.keys()):
                    attrs = {k: issuedAttributes[k] for k in claimAttrs}
            matchingLinkAndReceivedClaim.append((li, cl, attrs))
        return matchingLinkAndReceivedClaim

    async def getMatchingRcvdClaimsAsync(self, attributes):
        linksAndReceivedClaim = await self.getMatchingLinksWithReceivedClaimAsync()
        attributes = set(attributes)

        matchingLinkAndRcvdClaim = []
        for li, cl, issuedAttrs in linksAndReceivedClaim:
            if attributes.intersection(issuedAttrs.keys()):
                matchingLinkAndRcvdClaim.append((li, cl, issuedAttrs))
        return matchingLinkAndRcvdClaim
