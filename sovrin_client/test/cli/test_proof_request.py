import pytest


@pytest.mark.skip('INDY-85. Not implemented yet')
def test_show_nonexistant_proof_request(be, do, aliceCLI):
    be(aliceCLI)
    do("show proof request Transcript", expect=["No matching proof request(s) found in current keyring"])
