import os
import sovrin_client
from plenum.common.pkg_util import check_deps

check_deps(sovrin_client)

from sovrin_common.plugin_helper import writeAnonCredPlugin
BASE_DIR = os.path.join(os.path.expanduser("~"), ".sovrin")
writeAnonCredPlugin(BASE_DIR)