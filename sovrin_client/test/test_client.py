
# This is very dumb test to start with, so need to come back to this one.
from sovrin_client.client import Client
from sovrin_node.node import Node


def testClient():
    c1 = Client()
    assert c1 is not None


def testNode():
    n1 = Node()
    c1 = Client()
    n1.dummy()
    c1.dummy()
