import logging
import time
import os

from sovrin_client.test.agent.bulldog_helper import getBulldogLogger
from sovrin_common.config import agentLoggingLevel


def createTdirIfNotCreated(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


def testLoggerLevelSuccess(tdir):
    createTdirIfNotCreated(tdir)
    logger = getBulldogLogger(tdir)
    filePath = '{}/bulldog_test.log'.format(tdir)
    formatter = logging.Formatter('%(asctime)s %(message)s')
    fileHandler = logging.FileHandler(filePath, mode='a')
    fileHandler.setLevel(agentLoggingLevel)
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
    logger.warn("warning")
    logger.debug("debug_logs_are_off")
    time.sleep(2)
    file = open(filePath, 'r')
    txt = file.read()
    arr = txt.split(" ")
    if any("debug_logs_are_off" in word for word in arr):
        assert False
    else:
        assert True


def testLoggerLevelError(tdir):
    createTdirIfNotCreated(tdir)
    logger = getBulldogLogger(tdir)
    logger.setLevel(logging.DEBUG)
    filePath = '{}/bulldog_test_fail.log'.format(tdir)
    formatter = logging.Formatter('%(asctime)s %(message)s')
    fileHandler = logging.FileHandler(filePath, mode='a')
    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
    logger.debug("debug_logs_are_on")
    logger.warn("warning")
    file = open(filePath, 'r')
    txt = file.read()
    arr = txt.split(" ")
    if any("debug_logs_are_on" in word for word in arr):
        assert True
    else:
        assert False
