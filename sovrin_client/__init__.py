import os
import sovrin_client

from sovrin_client.agent.jsonpickle_util import setUpJsonpickle
from .__metadata__ import *

from sovrin_common.plugin_helper import writeAnonCredPlugin
BASE_DIR = os.path.join(os.path.expanduser("~"), ".sovrin")
writeAnonCredPlugin(BASE_DIR)


# Loading charm crypto so that corresponding stored wallet data
# can be restored correctly. Setting up some custom handlers so that
# it can handle charm crypto type integer.Element

from config.config import cmod
setUpJsonpickle()