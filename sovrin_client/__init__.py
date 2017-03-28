import os
import sovrin_client

import importlib
from .__metadata__ import *

from sovrin_common.plugin_helper import writeAnonCredPlugin
BASE_DIR = os.path.join(os.path.expanduser("~"), ".sovrin")
writeAnonCredPlugin(BASE_DIR)