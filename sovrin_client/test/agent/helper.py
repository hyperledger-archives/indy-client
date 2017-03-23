import argparse
import sys

from plenum.common.signer_simple import SimpleSigner
from plenum.common.eventually import eventually
from plenum.test.test_stack import checkRemoteExists, CONNECTED

from sovrin_client.client.wallet.wallet import Wallet


def connectAgents(agent1, agent2):
    e1 = agent1.endpoint
    e2 = agent2.endpoint
    e1.connectTo(e2.ha)


def ensureAgentsConnected(looper, agent1, agent2):
    e1 = agent1.endpoint
    e2 = agent2.endpoint
    looper.run(eventually(checkRemoteExists, e1, e2.name, CONNECTED,
                          timeout=10))
    looper.run(eventually(checkRemoteExists, e2, e1.name, CONNECTED,
                          timeout=10))

    
def buildAgentWallet(name, seed):
    wallet = Wallet(name)
    wallet.addIdentifier(signer=SimpleSigner(seed=seed))
    return wallet


def buildFaberWallet():
    return buildAgentWallet("FaberCollege", b'Faber000000000000000000000000000')


def buildAcmeWallet():
    return buildAgentWallet("AcmeCorp", b'Acme0000000000000000000000000000')


def buildThriftWallet():
    return buildAgentWallet("ThriftBank", b'Thrift00000000000000000000000000')


async def bootstrap_schema(agent, attrib_def_name, schema_name, schema_version, p_prime, q_prime):
    schema_id = await agent.publish_schema(attrib_def_name,
                                           schema_name=schema_name,
                                           schema_version=schema_version)

    _, _ = await agent.publish_issuer_keys(schema_id, p_prime=p_prime, q_prime=q_prime)

    await agent.publish_revocation_registry(schema_id=schema_id)

    return schema_id