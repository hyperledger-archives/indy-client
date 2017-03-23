import json
from sovrin_client.agent.agent import WalletedAgent
from sovrin_client.test.agent.mock_backend_system import MockBackendSystem

import anoncreds.protocol.types
from plenum.common.member.steward import Steward
from plenum.common.util import adict
from sovrin_client.client.client import Client
from sovrin_client.client.wallet.wallet import Wallet
from sovrin_client.test.helper import primes
from sovrin_common.identity import Identity
from sovrin_common.init_util import initialize_node_environment
from sovrin_common.constants import TRUST_ANCHOR
from sovrin_node.server.node import Node
from sovrin_node.pool.local_pool import LocalPool

# noinspection PyUnresolvedReferences
from sovrin_node.test.conftest import tdir, conf, nodeSet, tconf, \
    updatedPoolTxnData, updatedDomainTxnFile, txnPoolNodeSet, poolTxnData, \
    nodeAndClientInfoFilePath, dirName, tdirWithDomainTxns, tdirWithPoolTxns, \
    domainTxnOrderedFields, genesisTxns, stewardWallet, poolTxnStewardData, \
    poolTxnStewardNames, trusteeWallet, trusteeData, poolTxnTrusteeNames, \
    patchPluginManager, txnPoolNodesLooper, tdirWithPoolTxns, \
    poolTxnNodeNames, allPluginsPath, tdirWithNodeKeepInited, testNodeClass, \
    genesisTxns


class RefAgent(WalletedAgent):

    def create_link(self, internal_id):

        nonce = str(self.verifier.generateNonce())
        endpoint = self.endpoint.host_address()
        endpoint = "127.0.0.1" + ":" + str(self.endpoint.ha[1])  #TODO: this should be done by endpoint

        msg = {'link-invitation': {
            'name': self.name,
            'identifier': self._wallet.defaultId,
            'nonce': nonce,
            'endpoint': endpoint,
            'verkey': self._wallet.getVerkey(self.wallet.defaultId)
            },
            'sig': None
        }

        self._invites[nonce] = internal_id

        signature = self.wallet.signMsg(msg, self.wallet.defaultId)

        msg['sig'] = signature

        return json.dumps(msg)


def test_end_to_end(tconf):
    print('*' * 20)
    print(tconf.baseDir)
    print('*' * 20)
    base_dir = tconf.baseDir

    w1 = Wallet()
    s1 = Steward(wallet=w1)
    s1.wallet.addIdentifier()

    w2 = Wallet()
    s2 = Steward(wallet=w2)
    s2.wallet.addIdentifier()

    w3 = Wallet()
    s3 = Steward(wallet=w3)
    s3.wallet.addIdentifier()

    w4 = Wallet()
    s4 = Steward(wallet=w4)
    s4.wallet.addIdentifier()

    # This sets up a node's secure communications and initializes keys. In a
    # real network, each of the following would be run by different stewards on
    # their respective node hosts

    n1_config = adict(name='Node1',
                      basedirpath=base_dir,
                      ha=('127.0.0.1', 9701),
                      cliha=('127.0.0.1', 9702))

    n2_config = adict(name='Node2',
                      basedirpath=base_dir,
                      ha=('127.0.0.1', 9703),
                      cliha=('127.0.0.1', 9704))

    n3_config = adict(name='Node3',
                      basedirpath=base_dir,
                      ha=('127.0.0.1', 9705),
                      cliha=('127.0.0.1', 9706))

    n4_config = adict(name='Node4',
                      basedirpath=base_dir,
                      ha=('127.0.0.1', 9707),
                      cliha=('127.0.0.1', 9708))

    # this is run only the first time the node is created
    n1_verkey = initialize_node_environment(name=n1_config.name,
                                            base_dir=n1_config.basedirpath,
                                            override_keep=True,
                                            config=tconf)
    n2_verkey = initialize_node_environment(name=n2_config.name,
                                            base_dir=n2_config.basedirpath,
                                            override_keep=True,
                                            config=tconf)
    n3_verkey = initialize_node_environment(name=n3_config.name,
                                            base_dir=n3_config.basedirpath,
                                            override_keep=True,
                                            config=tconf)
    n4_verkey = initialize_node_environment(name=n4_config.name,
                                            base_dir=n4_config.basedirpath,
                                            override_keep=True,
                                            config=tconf)

    s1.set_node(n1_config, verkey=n1_verkey)
    s2.set_node(n2_config, verkey=n2_verkey)
    s3.set_node(n3_config, verkey=n3_verkey)
    s4.set_node(n4_config, verkey=n4_verkey)

    genesis_txns = s1.generate_genesis_txns() + \
                   s2.generate_genesis_txns() + \
                   s3.generate_genesis_txns() + \
                   s4.generate_genesis_txns()

    with LocalPool(genesis_txns, base_dir) as network:
        genesis_files = network.generate_genesis_files()

        print(genesis_files)

        # TODO the Nodes and Clients all rely on the files created with the
        # command above; they should be packaged up and delivered to the Nodes
        # and Client.

        n1 = Node(**n1_config)
        n2 = Node(**n2_config)
        n3 = Node(**n3_config)
        n4 = Node(**n4_config)

        network.add(n1)
        network.add(n2)
        network.add(n3)
        network.add(n4)

        network.runFor(5)

        client = Client(basedirpath=base_dir,
                        ha=('127.0.0.1', 5555))

        bank_wallet = Wallet()
        bank_agent = RefAgent(name="bank",
                              basedirpath=base_dir,
                              client=client,
                              wallet=bank_wallet,
                              port=8787)

        network.add(bank_agent)

        bank_id, bank_verkey = bank_agent.new_identifier()

        print(bank_id)
        print(bank_verkey)

        # bank transfers identity out-of-band to the steward
        s1_agent = RefAgent(name="steward1",
                            basedirpath=base_dir,
                            client=client,
                            wallet=w1,
                            port=8781)

        network.add(s1_agent)

        s1_agent.publish_trust_anchor(Identity(identifier=bank_id,
                                               verkey=bank_verkey,
                                               role=TRUST_ANCHOR))
        network.runFor(5)

        # this allows calling asynchronous functions from a synchronous context
        run_async = network.run

        bank_attribute_definition = \
            anoncreds.protocol.types.AttribDef('basic',
                                               [anoncreds.protocol.types.AttribType('title', encode=True),
                                                anoncreds.protocol.types.AttribType('first_name', encode=True),
                                                anoncreds.protocol.types.AttribType('last_name', encode=True),
                                                anoncreds.protocol.types.AttribType('address_1', encode=True),
                                                anoncreds.protocol.types.AttribType('address_2', encode=True),
                                                anoncreds.protocol.types.AttribType('address_3', encode=True),
                                                anoncreds.protocol.types.AttribType('postcode_zip', encode=True),
                                                anoncreds.protocol.types.AttribType('date_of_birth', encode=True),
                                                anoncreds.protocol.types.AttribType('account_type', encode=True),
                                                anoncreds.protocol.types.AttribType('year_opened', encode=True),
                                                anoncreds.protocol.types.AttribType('account_status', encode=True)])

        bank_agent.add_attribute_definition(bank_attribute_definition)

        backend = MockBackendSystem(bank_attribute_definition)

        alices_id_in_banks_system = 1999891343
        bobs_id_in_banks_system = 2911891343

        backend.add_record(alices_id_in_banks_system,
                           title='Mrs.',
                           first_name='Alicia',
                           last_name='Garcia',
                           address_1='H-301',
                           address_2='Street 1',
                           address_3='UK',
                           postcode_zip='G61 3NR',
                           date_of_birth='December 28, 1990',
                           account_type='savings',
                           year_opened='2000',
                           account_status='active')
        backend.add_record(bobs_id_in_banks_system,
                           title='Mrs.',
                           first_name='Jay',
                           last_name='Raj',
                           address_1='222',
                           address_2='Baker Street',
                           address_3='UK',
                           postcode_zip='G61 3NR',
                           date_of_birth='January 15, 1980',
                           account_type='savings',
                           year_opened='1999',
                           account_status='active')

        bank_agent.set_issuer_backend(backend)

        schema_id = run_async(
            bank_agent.publish_schema('basic',
                                      schema_name='Bank Membership',
                                      schema_version='1.0'))

        # NOTE: do NOT use known primes in a non-test environment

        issuer_pub_key, revocation_pub_key = run_async(
            bank_agent.publish_issuer_keys(schema_id,
                                           p_prime=primes["prime1"][0],
                                           q_prime=primes["prime1"][1]))
        print(issuer_pub_key)
        print(revocation_pub_key)

        accPK = run_async(bank_agent.publish_revocation_registry(
            schema_id=schema_id))

        print(accPK)

        run_async(bank_agent.set_available_claim(alices_id_in_banks_system, schema_id))
        run_async(bank_agent.set_available_claim(bobs_id_in_banks_system, schema_id))

        alice_wallet = Wallet()
        alice_agent = RefAgent(name="Alice",
                               basedirpath=base_dir,
                               client=client,
                               wallet=alice_wallet,
                               port=8786)

        network.add(alice_agent)

        network.runFor(1)

        invitation = bank_agent.create_link(alices_id_in_banks_system)

        # Transfer of this invitation happens out-of-band (website, QR code, etc)

        alices_link_to_bank = alice_agent.load_invitation_str(invitation)

        # notice the link is not accepted
        print(alices_link_to_bank)

        alice_agent.accept_invitation(alices_link_to_bank)

        network.runFor(3)

        # notice that the link is accepted
        print(alices_link_to_bank)

        banks_link_to_alice = bank_agent.get_link_by_name(alices_id_in_banks_system)

        # note the available claims are now there
        print(banks_link_to_alice)

        claim_to_request = alices_link_to_bank.find_available_claim(name='Bank Membership')

        print(claim_to_request)

        run_async(alice_agent.send_claim(alices_link_to_bank,
                                         claim_to_request))
        network.runFor(3)

        claim = run_async(alice_agent.get_claim(schema_id))
        print(claim)


