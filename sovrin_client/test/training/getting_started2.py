import os

from sovrin_common.config_util import getConfig

from plenum.common.plugin_helper import loadPlugins
from sovrin_client.cli.cli import SovrinCli
from sovrin_client.test.training.getting_started import demo_start_agents, demo_setup_logging
from sovrin_node.pool.local_pool import create_local_pool

config = getConfig()
base_dir = config.baseDir
if not os.path.exists(base_dir):
    os.makedirs(base_dir)
loadPlugins(base_dir)


def main():
    demo_setup_logging(base_dir)

    pool = create_local_pool(base_dir)

    demo_start_agents(pool, pool, pool.base_dir )

    curDir = os.getcwd()
    logFilePath = os.path.join(curDir, config.logFilePath)

    # Instead of running agent for the user (say for Alice),
    # run cli which internally runs agent
    cli = SovrinCli(looper=pool,
                    basedirpath=pool.base_dir,
                    logFileName=logFilePath,
                    withNode=False
                    )

    pool.run(cli.shell())

if __name__ == "__main__":
    main()
