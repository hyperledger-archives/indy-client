import logging

from os.path import expanduser, exists
from logging import getLogger

from sovrin_common.config_util import getConfig
from sovrin_common.config import agentLoggingLevel


bulldogLoggerMap = {}


def getBulldogLogger(basedirpath=None):
    key = basedirpath or 'default'
    logger = bulldogLoggerMap.get(key)
    if logger:
        return logger

    basedir = basedirpath or getConfig().baseDir
    path = expanduser('{}'.format(basedir))
    filePath = '{}/bulldog.log'.format(path)

    try:
        if not exists(filePath):
            with open(filePath, mode='a+'):
                # we just want to create a file if not exists
                # don't do anything else with file handler
                pass

        log = getLogger()
        log.setLevel(agentLoggingLevel)

        formatter = logging.Formatter('%(asctime)s %(message)s')
        fileHandler = logging.FileHandler(filePath, mode='a')
        fileHandler.setLevel(agentLoggingLevel)
        fileHandler.setFormatter(formatter)
        log.addHandler(fileHandler)

        bulldogLoggerMap[key] = log
        return log
    except OSError as e:
        print('Could not create log file: {}'.format(str(e)))
        raise Exception



