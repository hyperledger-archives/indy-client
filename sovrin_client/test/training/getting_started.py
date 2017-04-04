# Test for required installed modules
import sys
try:
    from sovrin_client import *
except ImportError as e:
    print("Sovrin Client is required for this guild, "
          "see doc for installing Sovrin Client.", file=sys.stderr)
    print(str(e), file=sys.stderr)
    sys.exit(-1)

try:
    from sovrin_node import *
except ImportError as e:
    print("Sovrin Node is required for this guild, "
          "see doc for installing Sovrin Node.", file=sys.stderr)
    print(str(e), file=sys.stderr)
    sys.exit(-1)

from sovrin_client.test.agent.acme import create_acme, bootstrap_acme
from sovrin_client.test.agent.faber import create_faber, bootstrap_faber
from sovrin_client.test.agent.thrift import create_thrift, bootstrap_thrift
from sovrin_common.constants import TRUST_ANCHOR
from sovrin_common.identity import Identity

# noinspection PyUnresolvedReferences
from sovrin_node.pool.local_pool import create_local_pool
# noinspection PyUnresolvedReferences
from sovrin_client.agent.agent import WalletedAgent
# noinspection PyUnresolvedReferences
from sovrin_client.client.wallet.wallet import Wallet
# noinspection PyUnresolvedReferences
from tempfile import TemporaryDirectory

from logging import Formatter
from plenum.common.log import Logger
from ioflo.base.consoling import Console
from plenum.config import logFormat

ignored_files = ['node.py', 'stacked.py', 'primary_elector.py',
                 'replica.py', 'propagator.py', 'upgrader.py',
                 'plugin_loader.py']

log_out_format = Formatter(fmt=logFormat, style="{")


def out(record, extra_cli_value=None):
    if record.filename not in ignored_files:
        print(log_out_format.format(record))

Logger().enableCliLogging(out, override_tags={})
Logger().setupRaet(raet_log_level=Console.Wordage.concise)


def start_agents(pool, looper):
    start_agent(create_faber, bootstrap_faber,
                pool.create_client(5500), looper,
                pool.steward_agent())

    start_agent(create_acme, bootstrap_acme,
                pool.create_client(5501), looper,
                pool.steward_agent())

    start_agent(create_thrift, bootstrap_thrift,
                pool.create_client(5502), looper,
                pool.steward_agent())


def start_agent(create_func, bootstrap_func, client, looper, steward):
    looper.run_till_quiet(1)
    agent = create_func(base_dir_path=None, client=client)
    looper.add(agent)

    steward.publish_trust_anchor(Identity(identifier=agent.wallet.defaultId,
                                          verkey=agent.wallet.getVerkey(agent.wallet.defaultId),
                                          role=TRUST_ANCHOR))
    looper.run_till_quiet(1)

    looper.run(bootstrap_func(agent))

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