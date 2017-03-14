import json

from plenum.common.roles import Roles
from plenum.common.txn import VERKEY, DATA, NODE, TYPE
from plenum.test.cli.helper import checkCmdValid

from sovrin_common.txn import NYM
from sovrin_common.txn import TARGET_NYM, ROLE


def executeAndCheckGenTxn(cli, cmd, typ, nym, role=None, data=None):
    checkCmdValid(cli, cmd)
    nymCorrect = False
    roleCorrect = False if role else True
    dataCorrect = False if data else True
    typeCorrect = False if typ else True

    role = Roles[role].value if role else role
    for txn in cli.genesisTransactions:
        if txn.get(TARGET_NYM) == nym:
            nymCorrect = True
            if txn.get(TYPE) == typ:
                typeCorrect = True
            if txn.get(ROLE) == role:
                roleCorrect = True
            if data and txn.get(DATA) == json.loads(data):
                dataCorrect = True

    assert typeCorrect and nymCorrect and roleCorrect and dataCorrect
    assert "Genesis transaction added" in cli.lastCmdOutput


def prepareCmdAndCheckGenTxn(cli, typ, nym, role=None, data=None):
    cmd = "add genesis transaction {} dest={}".format(typ, nym)
    if role:
        cmd += " role={}".format(role)
    if data:
        cmd += " with data {}".format(data)
    executeAndCheckGenTxn(cli, cmd, typ, nym, role, data)


def testAddGenTxnBasic(cli):
    nym = "2ru5PcgeQzxF7QZYwQgDkG2K13PRqyigVw99zMYg8eML"
    role = None
    typ = NYM
    prepareCmdAndCheckGenTxn(cli, typ, nym, role)


def testAddGenTxnWithRole(cli):
    nym = "2ru5PcgeQzxF7QZYwQgDkG2K13PRqyigVw99zMYg8eML"
    role = Roles.STEWARD.name
    typ = NYM
    prepareCmdAndCheckGenTxn(cli, typ, nym, role)


def testAddGenTxnForNode(cli):
    nym = "2ru5PcgeQzxF7QZYwQgDkG2K13PRqyigVw99zMYg8eML"
    by = "FvDi9xQZd1CZitbK15BNKFbA7izCdXZjvxf91u3rQVzW"
    role = None
    typ = NODE
    data = '{"node_ip": "localhost", "node_port": "9701", "client_ip": "localhost", "client_port": "9702", "alias": "AliceNode"}'
    cmd = 'add genesis transaction {} for {} by {} with data {}'.format(typ, nym, by, data)
    executeAndCheckGenTxn(cli, cmd, typ, nym, role, data)

