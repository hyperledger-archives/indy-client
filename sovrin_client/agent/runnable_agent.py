import sys
import argparse

from sovrin_client.client.client import Client
from sovrin_client.agent.agent import createAgent, runAgent, Agent
from plenum.common.log import getlogger
from plenum.common.util import getFormattedErrorMsg

logger = getlogger()


class RunnableAgent:
    @classmethod
    def get_passed_args(cls):
        return cls.parser_cmd_args()

    @classmethod
    def parser_cmd_args(cls):
        if sys.stdin.isatty():
            parser = argparse.ArgumentParser(
                description="Starts agents with given port, cred def and issuer seq")

            parser.add_argument('--port', required=False,
                                help='port where agent will listen')

            args = parser.parse_args()
            port = int(args.port) if args.port else None
            return port,
        else:
            return None,

    @classmethod
    def run_agent(cls, agent: Agent, looper=None, bootstrap=None):
        try:
            loop = looper.loop if looper else None
            agent.loop = loop
            runAgent(agent, looper, bootstrap)
            return agent
        except Exception as exc:
            error = "Agent startup failed: [cause : {}]".format(str(exc))
            logger.error(getFormattedErrorMsg(error))