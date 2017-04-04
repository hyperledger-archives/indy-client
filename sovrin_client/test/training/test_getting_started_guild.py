from sovrin_client.test.training.getting_started import *

# noinspection PyUnresolvedReferences
from sovrin_node.test.conftest import tconf

def test_getting_started(tconf):
    getting_started(base_dir=tconf.baseDir)


def getting_started(base_dir=None):
    ####################################
    #  Setup
    ####################################

    if base_dir is None:
        base_dir = TemporaryDirectory().name

    pool = create_local_pool(base_dir)

    start_agents(pool, pool)

    ####################################
    #  Alice's Wallet
    ####################################

    alice_wallet = Wallet()
    alice_agent = WalletedAgent(name="Alice",
                                basedirpath=base_dir,
                                client=pool.create_client(5403),
                                wallet=alice_wallet,
                                port=8786)

    pool.add(alice_agent)

    pool.run_till_quiet()

    ####################################
    #  Faber Invitation
    ####################################

    print(FABER_INVITE)

    link_to_faber = alice_agent.load_invitation_str(FABER_INVITE)

    print(link_to_faber)

    alice_agent.accept_invitation(link_to_faber)

    pool.run_till_quiet()

    print(link_to_faber)

    alice_agent.sendPing("Faber College")

    pool.run_till_quiet(2)

    ####################################
    #  Transcription Claim
    ####################################

    claim_to_request = link_to_faber.find_available_claim(name='Transcript')

    print(claim_to_request)

    pool.run(alice_agent.send_claim(link_to_faber, claim_to_request))

    pool.run_till_quiet()

    claims = pool.run(alice_agent.prover.wallet.getAllClaims())

    print(claims)

    ####################################
    #  Acme Invitation
    ####################################

    link_to_acme = alice_agent.load_invitation_str(ACME_INVITE)

    print(link_to_acme)

    alice_agent.accept_invitation(link_to_acme)

    pool.run_till_quiet()

    print(link_to_acme)

    job_application_request = link_to_acme.find_proof_request(name='Job-Application')

    print(job_application_request)

    alice_agent.sendProof(link_to_acme, job_application_request)

    pool.run_till_quiet(2)

    print(link_to_acme)

    ####################################
    #  Job-Certificate Claim
    ####################################

    job_certificate = link_to_acme.find_available_claim(name='Job-Certificate')

    print(job_certificate)

    pool.run(alice_agent.send_claim(link_to_acme, job_certificate))

    pool.run_till_quiet()

    claims = pool.run(alice_agent.prover.wallet.getAllClaims())

    print(claims)

    ####################################
    #  Acme Invitation
    ####################################

    link_to_thrift = alice_agent.load_invitation_str(THRIFT_INVITE)

    print(link_to_thrift)

    alice_agent.accept_invitation(link_to_thrift)

    pool.run_till_quiet()

    print(link_to_thrift)

    ####################################
    #  Proof to Thrift
    ####################################

    load_basic_request = link_to_thrift.find_proof_request(name='Loan-Application-Basic')

    print(load_basic_request)

    alice_agent.sendProof(link_to_thrift, load_basic_request)

    pool.run_till_quiet()

    print(link_to_thrift)

    ########

    load_kyc_request = link_to_thrift.find_proof_request(name='Loan-Application-KYC')

    print(load_kyc_request)

    alice_agent.sendProof(link_to_thrift, load_kyc_request)

    pool.run_till_quiet()

    print(link_to_thrift)

if __name__ == "__main__":
    getting_started()
