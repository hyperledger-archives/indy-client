from plenum.common.log import getlogger
from sovrin_client.agent.runnable_agent import RunnableAgent
from sovrin_client.agent.agent import create_client
from sovrin_client.test.agent.mock_backend_system import MockBackendSystem

from anoncreds.protocol.types import AttribType, AttribDef
from sovrin_client.agent.agent import WalletedAgent
from sovrin_client.test.helper import primes
from sovrin_client.test.agent.helper import buildFaberWallet
from sovrin_client.test.helper import TestClient

logger = getlogger()


def create_faber(name=None, wallet=None, base_dir_path=None, port=None):

    client = create_client(base_dir_path=None, client_class=TestClient)

    agent = WalletedAgent(name=name or "Faber College",
                       basedirpath=base_dir_path,
                       client=client,
                       wallet=wallet or buildFaberWallet(),
                       port=port)

    agent._invites = {
        "b1134a647eb818069c089e7694f63e6d": 1,
        "2a2eb72eca8b404e8d412c5bf79f2640": 2,
        "7513d1397e87cada4214e2a650f603eb": 3,
        "710b78be79f29fc81335abaa4ee1c5e8": 4
    }

    transcript_def = AttribDef('Transcript',
                              [AttribType('student_name', encode=True),
                               AttribType('ssn', encode=True),
                               AttribType('degree', encode=True),
                               AttribType('year', encode=True),
                               AttribType('status', encode=True)])

    agent.add_attribute_definition(transcript_def)

    backend = MockBackendSystem(transcript_def)

    backend.add_record(1,
                       student_name="Alice Garcia",
                       ssn="123-45-6789",
                       degree="Bachelor of Science, Marketing",
                       year="2015",
                       status="graduated")

    backend.add_record(2,
                       student_name="Carol Atkinson",
                       ssn="783-41-2695",
                       degree="Bachelor of Science, Physics",
                       year="2012",
                       status="graduated")

    backend.add_record(3,
                       student_name="Frank Jeffrey",
                       ssn="996-54-1211",
                       degree="Bachelor of Arts, History",
                       year="2013",
                       status="dropped")

    backend.add_record(4,
                       student_name="Craig Richards",
                       ssn="151-44-5876",
                       degree="MBA, Finance",
                       year="2015",
                       status="graduated")

    agent.set_issuer_backend(backend)

    return agent

async def bootstrap_faber(agent):
    schema_id = await agent.publish_schema('Transcript',
                                           schema_name='Transcript',
                                           schema_version='1.2')

    # NOTE: do NOT use known primes in a non-test environment
    issuer_pub_key, revocation_pub_key = await agent.publish_issuer_keys(schema_id,
                                                                         p_prime=primes["prime1"][0],
                                                                         q_prime=primes["prime1"][1])
    print(issuer_pub_key)
    print(revocation_pub_key)

    accPK = await agent.publish_revocation_registry(schema_id=schema_id)

    print(accPK)

    await agent.set_available_claim(1, schema_id)
    await agent.set_available_claim(2, schema_id)
    await agent.set_available_claim(3, schema_id)
    await agent.set_available_claim(4, schema_id)


if __name__ == "__main__":
    port = RunnableAgent.parser_cmd_args()
    if port is None:
        port = 5555
    agent = create_faber(name="Faber College", wallet=buildFaberWallet(), base_dir_path=None, port=port)
    RunnableAgent.run_agent(agent, bootstrap=bootstrap_faber(agent))

