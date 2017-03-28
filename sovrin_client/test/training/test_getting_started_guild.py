import json

from sovrin_client.test.agent.acme import create_acme, bootstrap_acme
from sovrin_client.test.agent.faber import create_faber, bootstrap_faber

from plenum.common.member.steward import Steward
from plenum.common.util import adict
from sovrin_client.client.client import Client
from sovrin_client.client.wallet.wallet import Wallet
from sovrin_client.test.agent.thrift import create_thrift, bootstrap_thrift
from sovrin_common.identity import Identity
from sovrin_common.init_util import initialize_node_environment
from sovrin_common.constants import TRUST_ANCHOR
from sovrin_node.server.node import Node
from sovrin_node.pool.local_pool import LocalPool
from unicorn.test.agent import RefAgent

# noinspection PyUnresolvedReferences
from sovrin_node.test.conftest import tdir, conf, nodeSet, tconf, \
    updatedPoolTxnData, updatedDomainTxnFile, txnPoolNodeSet, poolTxnData, \
    nodeAndClientInfoFilePath, dirName, tdirWithDomainTxns, tdirWithPoolTxns, \
    domainTxnOrderedFields, genesisTxns, stewardWallet, poolTxnStewardData, \
    poolTxnStewardNames, trusteeWallet, trusteeData, poolTxnTrusteeNames, \
    patchPluginManager, txnPoolNodesLooper, tdirWithPoolTxns, \
    poolTxnNodeNames, allPluginsPath, tdirWithNodeKeepInited, testNodeClass, \
    genesisTxns

FABER_INVITE = """
{
  "link-invitation": {
    "name": "Faber College",
    "identifier": "FuN98eH2eZybECWkofW6A9BKJxxnTatBCopfUiNxo6ZB",
    "nonce": "b1134a647eb818069c089e7694f63e6d",
    "endpoint": "127.0.0.1:5555"
  },
  "sig": "4QKqkwv9gXmc3Sw7YFkGm2vdF6ViZz9FKZcNJGh6pjnjgBXRqZ17Sk8bUDSb6hsXHoPxrzq2F51eDn1DKAaCzhqP"
}"""

THRIFT_INVITE = """
{
  "link-invitation": {
    "name": "Thrift Bank",
    "identifier": "9jegUr9vAMqoqQQUEAiCBYNQDnUbTktQY9nNspxfasZW",
    "nonce": "77fbf9dc8c8e6acde33de98c6d747b28c",
    "endpoint": "127.0.0.1:7777"
  },
  "proof-requests": [{
      "name": "Loan-Application-Basic",
      "version": "0.1",
      "attributes": {
            "salary_bracket": "string",
            "employee_status": "string"
       },
       "verifiableAttributes": ["salary_bracket", "employee_status"]
    }, {
      "name": "Loan-Application-KYC",
      "version": "0.1",
      "attributes": {
            "first_name": "string",
            "last_name": "string",
            "ssn": "string"
      },
      "verifiableAttributes": ["first_name", "last_name", "ssn"]
    }, {
      "name": "Name-Proof",
      "version": "0.1",
      "attributes": {
            "first_name": "string",
            "last_name": "string"
      },
      "verifiableAttributes": ["first_name", "last_name"]
    }],
  "sig": "D1vU5fbtJbqWKdCoVJgqHBLLhh5CYspikuEXdnBVVyCnLHiYC9ZsZrDWpz3GkFFGvfC4RQ4kuB64vUFLo3F7Xk6"
}
"""

ACME_INVITE = """
{
    "link-invitation": {
        "name": "Acme Corp",
        "identifier": "7YD5NKn3P4wVJLesAmA1rr7sLPqW9mR1nhFdKD518k21",
        "nonce": "57fbf9dc8c8e6acde33de98c6d747b28c",
        "endpoint": "127.0.0.1:6666"
    },
    "proof-requests": [{
      "name": "Job-Application",
      "version": "0.2",
      "attributes": {
          "first_name": "string",
          "last_name": "string",
          "phone_number": "string",
          "degree": "string",
          "status": "string",
          "ssn": "string"
      },
      "verifiableAttributes": ["degree", "status", "ssn"]
    }],
    "sig": "sdf"
}"""


def start_agent(create_func, bootstrap_func, client, looper, steward):
    agent = create_func(base_dir_path=None, client=client)
    looper.add(agent)

    steward.publish_trust_anchor(Identity(identifier=agent.wallet.defaultId,
                                          verkey=agent.wallet.getVerkey(agent.wallet.defaultId),
                                          role=TRUST_ANCHOR))
    looper.runFor(5)

    looper.run(bootstrap_func(agent))


def test_end_to_end(tconf):
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
                        ha=('127.0.0.1', 5005))

        s1_agent = RefAgent(name="steward1",
                            basedirpath=base_dir,
                            client=client,
                            wallet=w1,
                            port=8781)

        network.add(s1_agent)

        start_agent(create_faber, bootstrap_faber, client, network, s1_agent)

        alice_wallet = Wallet()
        alice_agent = RefAgent(name="Alice",
                               basedirpath=base_dir,
                               client=client,
                               wallet=alice_wallet,
                               port=8786)

        network.add(alice_agent)

        network.runFor(1)



        # Transfer of this invitation happens out-of-band (website, QR code etc)
        alices_link_to_faber = alice_agent.load_invitation_str(FABER_INVITE)

        # notice the link is not accepted
        print(alices_link_to_faber)

        alice_agent.accept_invitation(alices_link_to_faber)

        network.runFor(1)

        print(alices_link_to_faber)

        alice_agent.sendPing("Faber College")

        network.runFor(1)

        claim_to_request = alices_link_to_faber.find_available_claim(
            name='Transcript')

        print(claim_to_request)

        network.run(alice_agent.send_claim(alices_link_to_faber,
                                           claim_to_request))

        network.runFor(1)

        claims = network.run(alice_agent.prover.wallet.getAllClaims())

        # TODO better printing of claims
        print(claims)

        start_agent(create_acme, bootstrap_acme, client, network, s1_agent)



        # Transfer of this invitation happens out-of-band (website, QR code etc)
        alices_link_to_acme = alice_agent.load_invitation_str(ACME_INVITE)

        # notice the link is not accepted
        print(alices_link_to_acme)

        alice_agent.accept_invitation(alices_link_to_acme)

        network.runFor(1)

        print(alices_link_to_acme)

        job_application_request = alices_link_to_acme.find_proof_request(name='Job-Application')

        print(job_application_request)

        alice_agent.sendProof(alices_link_to_acme, job_application_request)
        network.runFor(25)
        print(alices_link_to_acme)

        ####################################
        #  Job-Certificate Claim
        ####################################
        job_certificate = alices_link_to_acme.find_available_claim(name='Job-Certificate')

        print(job_certificate)

        network.run(alice_agent.send_claim(alices_link_to_acme,
                                           job_certificate))

        network.runFor(1)

        claims = network.run(alice_agent.prover.wallet.getAllClaims())

        # TODO better printing of claims
        print(claims)

        ####################################
        #  Proof to Thrift
        ####################################

        start_agent(create_thrift, bootstrap_thrift, client, network, s1_agent)

        network.runFor(1)

        alices_link_to_thrift = alice_agent.load_invitation_str(THRIFT_INVITE)

        # notice the link is not accepted
        print(alices_link_to_thrift)

        alice_agent.accept_invitation(alices_link_to_thrift)

        network.runFor(1)

        print(alices_link_to_thrift)

        load_basic_request = alices_link_to_thrift.find_proof_request(name='Loan-Application-Basic')

        print(load_basic_request)

        alice_agent.sendProof(alices_link_to_thrift, load_basic_request)
        network.runFor(25)
        print(alices_link_to_thrift)

        ########

        load_kyc_request = alices_link_to_thrift.find_proof_request(name='Loan-Application-KYC')

        print(load_kyc_request)

        alice_agent.sendProof(alices_link_to_thrift, load_kyc_request)
        network.runFor(25)
        print(alices_link_to_thrift)

