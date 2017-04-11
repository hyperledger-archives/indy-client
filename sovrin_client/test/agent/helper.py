import argparse
import os
import sys

from stp_core.loop.eventually import eventually
from stp_core.loop.looper import Looper
from plenum.common.signer_simple import SimpleSigner
from sovrin_client.agent.agent import runBootstrap, runAgent
from sovrin_client.agent.agent_cli import AgentCli
from sovrin_client.client.wallet.wallet import Wallet
from sovrin_common.config_util import getConfig

config = getConfig()


def connectAgents(agent1, agent2):
    e1 = agent1.endpoint
    e2 = agent2.endpoint
    e1.connectTo(e2.ha)


def ensureAgentConnected(looper, agent, link):
    linkHa = link.getRemoteEndpoint(required=True)
    def _checkConnected():
        assert agent.endpoint.isConnectedTo(ha=linkHa)

    looper.run(eventually(_checkConnected, timeout=10))


def getAgentCmdLineParams():
    if sys.stdin.isatty():
        parser = argparse.ArgumentParser(
            description="Starts agents with given port, cred def and issuer seq")

        parser.add_argument('--port', required=False,
                            help='port where agent will listen')

        parser.add_argument('--withcli',
                            help='if given, agent will start in cli mode',
                            action='store_true')

        args = parser.parse_args()
        port = int(args.port) if args.port else None
        with_cli = args.withcli
        return port, with_cli
    else:
        return None, False

    
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

    # TODO not fully implemented yet!
    # await agent.publish_revocation_registry(schema_id=schema_id)

    return schema_id


def bootstrapAgentCli(name, agentCreator, looper, bootstrap):
    curDir = os.getcwd()
    logFilePath = os.path.join(curDir, config.logFilePath)
    cli = AgentCli(name='{}-Agent'.format(name).lower().replace(" ", "-"),
                   agentCreator=agentCreator,
                   looper=looper,
                   basedirpath=config.baseDir,
                   logFileName=logFilePath)
    if bootstrap:
        try:
            looper.run(runBootstrap(bootstrap(cli.agent)))
        except Exception as exc:
            error = "Agent startup failed: [cause : {}]".format(str(exc))
            cli.print(error)

    return cli


def runAgentCli(name, agentCreator, looper=None, bootstrap=True):
    def run(looper):
        agentCli = bootstrapAgentCli(name, agentCreator, looper, bootstrap)
        commands = sys.argv[1:]
        looper.run(agentCli.shell(*commands))

    if looper:
        run(looper)
    else:
        with Looper(debug=False) as looper:
            run(looper)


def startAgent(looper, agent, wallet, bootstrap=None):
    agent = agent
    wallet.pendSyncRequests()
    prepared = wallet.preparePending()
    agent.client.submitReqs(*prepared)

    runAgent(agent, looper, bootstrap=bootstrap)
    return agent, wallet
