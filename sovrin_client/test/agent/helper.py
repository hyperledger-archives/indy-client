import argparse
import os
import sys

from stp_core.loop.eventually import eventually
from sovrin_client.agent.endpoint import REndpoint, ZEndpoint
from stp_core.loop.looper import Looper
from plenum.common.signer_simple import SimpleSigner
from plenum.test.test_stack import checkRemoteExists, CONNECTED
from sovrin_client.agent.agent_cli import AgentCli
from sovrin_client.client.wallet.wallet import Wallet
from sovrin_common.config_util import getConfig

config = getConfig()


def connectAgents(agent1, agent2):
    e1 = agent1.endpoint
    e2 = agent2.endpoint
    e1.connectTo(e2.ha)


def ensureAgentsConnected(looper, agent1, agent2):
    e1 = agent1.endpoint
    e2 = agent2.endpoint
    if isinstance(e1, ZEndpoint) and isinstance(e2, ZEndpoint):
        def _(e1, e2):
            assert e1.publicKey in e2.remotesByKeys or e1.publicKey in e2.peersWithoutRemotes
            assert e2.publicKey in e1.remotesByKeys or e2.publicKey in e1.peersWithoutRemotes

        looper.run(eventually(_, e1, e2, timeout=10))

    elif isinstance(e1, REndpoint) and isinstance(e2, REndpoint):
        looper.run(eventually(checkRemoteExists, e1, e2.name, CONNECTED,
                              timeout=10))
        looper.run(eventually(checkRemoteExists, e2, e1.name, CONNECTED,
                              timeout=10))
    else:
        RuntimeError('Unacceptable Endpoint types')


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


def bootstrapAgentCli(name, agentCreator, looper, bootstrap):
    curDir = os.getcwd()
    logFilePath = os.path.join(curDir, config.logFilePath)
    cli = AgentCli(name='{}-Agent'.format(name).lower().replace(" ", "-"),
                   agentCreator=agentCreator,
                   looper=looper,
                   basedirpath=config.baseDir,
                   logFileName=logFilePath)
    if bootstrap:
        looper.run(cli.agent.bootstrap())

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
