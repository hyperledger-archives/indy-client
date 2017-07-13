def test_show_nonexistent_proof_request(be, do, aliceCLI):
    be(aliceCLI)
    do("show proof request Transcript", expect=["No matching Proof Requests found in current keyring"], within=1)
