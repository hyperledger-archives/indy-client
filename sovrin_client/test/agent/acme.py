from plenum.common.log import getlogger
from sovrin_client.agent.runnable_agent import RunnableAgent
from sovrin_client.agent.agent import create_client
from sovrin_client.test.agent.mock_backend_system import MockBackendSystem

from sovrin_client.agent.agent import WalletedAgent
from sovrin_client.test.helper import primes
from sovrin_client.test.agent.helper import buildFaberWallet, bootstrap_schema
from sovrin_client.test.helper import TestClient

from anoncreds.protocol.types import AttribType, AttribDef, ID

logger = getlogger()

schema_id = None


class AcmeAgent(WalletedAgent):
    async def postClaimVerif(self, claimName, link, frm):
        if claimName == "Job-Application":

            for schema in await self.issuer.wallet.getAllSchemas():

                if schema.name == 'Job-Certificate':
                    await self.set_available_claim(link.remoteIdentifier,
                                                   ID(schemaKey=schema.getKey(),
                                                      schemaId=schema.seqId))

                    claims = self.get_available_claim_list(link)
                    self.sendNewAvailableClaimsData(claims, frm, link)


def create_acme(name=None, wallet=None, base_dir_path=None, port=None):

    client = create_client(base_dir_path=None, client_class=TestClient)

    agent = AcmeAgent(name=name or "Faber College",
                       basedirpath=base_dir_path,
                       client=client,
                       wallet=wallet or buildFaberWallet(),
                       port=port)

    # maps invitation nonces to internal ids
    agent._invites = {
        "57fbf9dc8c8e6acde33de98c6d747b28c": 1,
        "3a2eb72eca8b404e8d412c5bf79f2640": 2,
        "8513d1397e87cada4214e2a650f603eb": 3,
        "810b78be79f29fc81335abaa4ee1c5e8": 4
    }

    job_cert_def = AttribDef('Job-Certificate',
                             [AttribType('first_name', encode=True),
                              AttribType('last_name', encode=True),
                              AttribType('employee_status', encode=True),
                              AttribType('experience', encode=True),
                              AttribType('salary_bracket', encode=True)])

    job_appl_def = AttribDef('Job-Application',
                             [AttribType('first_name', encode=True),
                              AttribType('last_name', encode=True),
                              AttribType('phone_number', encode=True),
                              AttribType('degree', encode=True),
                              AttribType('status', encode=True),
                              AttribType('ssn', encode=True)])

    agent.add_attribute_definition(job_cert_def)
    agent.add_attribute_definition(job_appl_def)

    backend = MockBackendSystem(job_cert_def)
    backend.add_record(1,
                       first_name="Alice",
                       last_name="Garcia",
                       employee_status="Permanent",
                       experience="3 years",
                       salary_bracket="between $50,000 to $100,000")

    backend.add_record(2,
                       first_name="Carol",
                       last_name="Atkinson",
                       employee_status="Permanent",
                       experience="2 years",
                       salary_bracket="between $60,000 to $90,000")

    backend.add_record(3,
                       first_name="Frank",
                       last_name="Jeffrey",
                       employee_status="Temporary",
                       experience="4 years",
                       salary_bracket="between $40,000 to $80,000")

    backend.add_record(4,
                       first_name="Craig",
                       last_name="Richards",
                       employee_status="On Contract",
                       experience="3 years",
                       salary_bracket="between $50,000 to $70,000")

    agent.set_issuer_backend(backend)

    return agent

async def bootstrap_acme(agent):
    await bootstrap_schema(agent,
                           'Job-Certificate',
                           'Job-Certificate',
                           '0.2',
                           primes["prime1"][0],
                           primes["prime1"][1])

    await bootstrap_schema(agent,
                           'Job-Application',
                           'Job-Application',
                           '0.2',
                           primes["prime2"][0],
                           primes["prime2"][1])


if __name__ == "__main__":
    args = RunnableAgent.parser_cmd_args()

    port = args[0]
    if port is None:
        port = 6666
    agent = create_acme(name='Acme Corp', wallet=buildFaberWallet(),
                        base_dir_path=None, port=port)
    RunnableAgent.run_agent(agent, bootstrap=bootstrap_acme(agent))

