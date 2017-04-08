from anoncreds.protocol.issuer import Issuer
from anoncreds.protocol.repo.attributes_repo import AttributeRepo
from anoncreds.protocol.repo.public_repo import PublicRepo
from anoncreds.protocol.wallet.issuer_wallet import IssuerWalletInMemory
from sovrin_client.anon_creds.sovrin_public_repo import SovrinPublicRepo
from sovrin_client.client.wallet.wallet import Wallet


class SovrinIssuer(Issuer):
    def __init__(self, client, wallet: Wallet, attrRepo: AttributeRepo,
                 publicRepo: PublicRepo = None):
        publicRepo = publicRepo or SovrinPublicRepo(client=client,
                                                    wallet=wallet)
        issuerWallet = IssuerWalletInMemory(wallet.name, publicRepo)
        super().__init__(issuerWallet, attrRepo)

    def prepareWalletForPersistence(self):
        # TODO: If we don't set self.wallet._repo.client to None,
        # it hangs during wallet persistence, based on findings, it seems,
        # somewhere it hangs during persisting client._ledger and
        # client.ledgerManager
        self.wallet._repo.client = None

    def restoreWallet(self, issuerWallet):
        curClient = self.wallet._repo.client
        self.wallet = issuerWallet
        self._primaryIssuer._wallet = issuerWallet
        self._nonRevocationIssuer._wallet = issuerWallet
        self.wallet._repo.client = curClient
