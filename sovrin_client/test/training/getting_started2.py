from tempfile import TemporaryDirectory

from sovrin_client.agent.runnable_agent import RunnableAgent
from sovrin_client.agent.walleted_agent import WalletedAgent
from sovrin_client.client.wallet.wallet import Wallet
from sovrin_client.test.training.getting_started import demo_start_agents, demo_setup_logging
from sovrin_node.pool.local_pool import create_local_pool


def main():
    base_dir = None
    if base_dir is None:
        base_dir = TemporaryDirectory().name

    demo_setup_logging(base_dir)

    pool = create_local_pool(base_dir)

    demo_start_agents(pool, pool, base_dir)

    client = pool.create_client(5403)

    alice_agent = WalletedAgent(name="Alice",
                                basedirpath=base_dir,
                                client=client,
                                wallet=Wallet(),
                                port=8786)

    RunnableAgent.run_agent(alice_agent, bootstrap=None, looper=None, with_cli=True)

if __name__ == "__main__":
    main()
