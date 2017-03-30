from sovrin_client.client.wallet.link import Link


def test_link_has_requested_proofs():
    testLink = Link("Test")

    # testLink.requestedProofs