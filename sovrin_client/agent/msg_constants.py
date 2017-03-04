ACCEPT_INVITE = 'ACCEPT_INVITE'
INVITE_ACCEPTED = "INVITE_ACCEPTED"

# Claims message types
CLAIM_OFFER = 'CLAIM_OFFER'
CLAIM_REQUEST = 'CLAIM_REQUEST'
CLAIM = 'CLAIM'
AVAIL_CLAIM_LIST = 'AVAIL_CLAIM_LIST'
REQ_AVAIL_CLAIMS = 'REQ_AVAIL_CLAIMS'

# TODO Why do we have this and AVAIL_CLAIM_LIST
NEW_AVAILABLE_CLAIMS = "NEW_AVAILABLE_CLAIMS"

# Proofs message types
PROOF_REQUEST = 'PROOF_REQUEST'
PROOF = 'PROOF'
PROOF_STATUS = 'PROOF_STATUS'


CLAIM_REQ_FIELD = 'claimReq'
CLAIM_FIELD = 'claim'
PROOF_FIELD = 'proof'
PROOF_INPUT_FIELD = 'proofInput'
REVEALED_ATTRS_FIELD = 'revealedAttrs'

# Other
CLAIM_NAME_FIELD = "claimName"
REF_REQUEST_ID = "refRequestId"

"""
ACCEPT_INVITE
{
    "type": 'ACCEPT_INVITE',
    "identifier": <id>,
    "nonce": <nonce>,
    "signature" : <sig>
}


AVAIL_CLAIM_LIST
{
    'type': 'AVAIL_CLAIM_LIST',
    'claims_list': [
        "Name": "Transcript",
        "Version": "1.2",
        "Definition": {
            "Attributes": {
                "student_name": "string",
                "ssn": "int",
                "degree": "string",
                "year": "string",
                "status": "string"
            }
        }
    ],
    "signature" : <sig>
}

AVAIL_CLAIM_LIST
{
    'type': 'AVAIL_CLAIM_LIST',
    'claims_list': [
        "Name": "Transcript",
        "Version": "1.2",
        "Definition": {
            "Attributes": {
                "student_name": "string",
                "ssn": "int",
                "degree": "string",
                "year": "string",
                "status": "string"
            }
        }
    ],
    "signature" : <sig>
}

"""
