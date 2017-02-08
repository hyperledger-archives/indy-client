import pytest
import logging
import time
import os

from sovrin_client.test.agent.bulldog_helper import bulldogLogger
from sovrin_common.config import agentLoggingLevel


def testLoggerLevelSuccess(tdir):
    logger = bulldogLogger
    filePath = '{}/bulldog_test.log'.format(tdir)
    formatter = logging.Formatter('%(asctime)s %(message)s')
    if not os.path.exists(tdir):
        os.makedirs(tdir)
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
    logger = bulldogLogger
    logger.setLevel(logging.DEBUG)
    filePath = '{}/bulldog_test_fail.log'.format(tdir)
    formatter = logging.Formatter('%(asctime)s %(message)s')
    if not os.path.exists(tdir):
        os.makedirs(tdir)
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
