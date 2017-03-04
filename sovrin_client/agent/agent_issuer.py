from abc import abstractmethod
from typing import Dict, Any

from plenum.common.txn import NAME, VERSION, ORIGIN
from plenum.common.types import f

from anoncreds.protocol.issuer import Issuer
from anoncreds.protocol.types import SchemaKey, ID
from anoncreds.protocol.types import ClaimRequest
from sovrin_client.agent.constants import EVENT_NOTIFY_MSG, CLAIMS_LIST_FIELD
from sovrin_client.agent.msg_constants import CLAIM, CLAIM_REQ_FIELD, CLAIM_FIELD, \
    AVAIL_CLAIM_LIST


class AgentIssuer:
    def __init__(self, issuer: Issuer):
        self.issuer = issuer

    async def processReqAvailClaims(self, msg):
        body, (frm, ha) = msg
        link = self.verifyAndGetLink(msg)
        acs = self.getAvailableClaimList(link.localIdentifier)
        data = {
            CLAIMS_LIST_FIELD: self.getAvailableClaimList(link.localIdentifier)
        }
        resp = self.getCommonMsg(AVAIL_CLAIM_LIST, data)
        self.signAndSend(resp, link.localIdentifier, frm)

    async def processReqClaim(self, msg):
        body, (frm, ha) = msg
        link = self.verifyAndGetLink(msg)
        if not link:
            raise NotImplementedError
        name = body[NAME]
        if not self.isClaimAvailable(link, name):
            self.notifyToRemoteCaller(
                EVENT_NOTIFY_MSG, "This claim is not yet available",
                self.issuer.wallet.defaultId, frm,
                origReqId=body.get(f.REQ_ID.nm))
            return

        version = body[VERSION]
        origin = body[ORIGIN]
        claimReq = ClaimRequest.fromStrDict(body[CLAIM_REQ_FIELD])

        schemaKey = SchemaKey(name, version, origin)
        schema = await self.issuer.wallet.getSchema(ID(schemaKey))
        schemaId = ID(schemaKey=schemaKey, schemaId=schema.seqId)

        self._addAtrribute(schemaKey=schemaKey, proverId=claimReq.userId,
                           link=link)

        claim = await self.issuer.issueClaim(schemaId, claimReq)

        claimDetails = {
            NAME: schema.name,
            VERSION: schema.version,
            CLAIM_FIELD: claim.toStrDict(),
            f.IDENTIFIER.nm: schema.issuerId
        }

        resp = self.getCommonMsg(CLAIM, claimDetails)
        self.signAndSend(resp, link.localIdentifier, frm,
                         origReqId=body.get(f.REQ_ID.nm))

    @abstractmethod
    def _addAtrribute(self, schemaKey, proverId, link) -> Dict[str, Any]:
        raise NotImplementedError
