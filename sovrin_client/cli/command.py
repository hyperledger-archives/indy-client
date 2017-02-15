from plenum.cli.command import Command

sendNymCmd = Command(
    id="send NYM",
    title="Adds given identifier to sovrin",
    syntax="send NYM dest=<target identifier> role=<role> [verkey=<ver-key>]",
    examples=[
        "send NYM dest=BiCMHDqC5EjheFHumZX9nuAoVEp8xyuBgiRi5JcY5whi role=SPONSOR",
        "send NYM dest=33A18XMqWqTzDpLHXLR5nT verkey=~Fem61Q5SnYhGVVHByQNxHj"])

sendGetNymCmd = Command(
    id="send GET_NYM",
    title="Get NYM from sovrin",
    syntax="send GET_NYM dest=<target identifier>",
    examples="send GET_NYM dest=33A18XMqWqTzDpLHXLR5nT")

sendAttribCmd = Command(
    id="send ATTRIB",
    title="Adds attributes to existing identifier",
    syntax="send ATTRIB dest=<target identifier> [raw={<json-data>}] [hash=<hashed-data>] [enc: <encrypted-data>]",
    examples='send ATTRIB dest=33A18XMqWqTzDpLHXLR5nT raw={"endpoint": "127.0.0.1:5555"}')


sendNodeCmd = Command(
    id="send NODE",
    title="Adds a node to the pool",
    syntax="send NODE dest=<target node identifier> data={<json-data>}",
    examples='send NODE dest=87Ys5T2eZfau4AATsBZAYvqwvD8XL5xYCHgg2o1ffjqg data={node_ip: 127.0.0.1, node_port: 9701, client_ip: 127.0.0.1, client_port: 9702, alias: test01}')


sendPoolUpgCmd = Command(
    id="send POOL_UPGRADE",
    title="Sends instructions to nodes to update themselves",
    syntax="send POOL_UPGRADE name=<name> version=<version> sha256=<sha256> action=<action> schedule=<schedule> timeout=<timeout>",
    examples="send POOL_UPGRADE name=upgrade-01 "
                              "version=0.0.1 sha256=aad1242 action=start "
                              "schedule={'AtDfpKFe1RPgcr5nnYBw1Wxkgyn8Zjyh5MzFoEUTeoV3': "
                              "'2017-01-25T12:49:05.258870+00:00', "
                              "'4yC546FFzorLPgTNTc6V43DnpFrR8uHvtunBxb2Suaa2': "
                              "'2017-01-25T12:33:53.258870+00:00', "
                              "'JpYerf4CssDrH76z7jyQPJLnZ1vwYgvKbvcp16AB5RQ': "
                              "'2017-01-25T12:44:01.258870+00:00', "
                              "'DG5M4zFm33Shrhjj6JB7nmx9BoNJUq219UXDfvwBDPe2': "
                              "'2017-01-25T12:38:57.258870+00:00'} "
                              "timeout=10")


sendSchemaCmd = Command(
    id="send SCHEMA",
    title="Adds schema to sovrin",
    syntax="send SCHEMA name=<schema-name> version=<version> type=<type> keys=<comma separated attributes>",
    examples="send SCHEMA name=Degree version=1.0 type=CL keys=undergrad,last_name,first_name,birth_date,postgrad,expiry_date")

sendIssuerCmd = Command(
    id="send ISSUER_KEY",
    title="Adds issuer keys for given schema",
    syntax="send ISSUER_KEY ref=<ref-no-of-SCHEMA-txn>",
    examples="send ISSUER_KEY ref=10")

showFileCmd = Command(
    id="show file",
    title="Shows content of given file",
    syntax="show <file-path>",
    examples="show sample/faber-invitation.sovrin")

loadFileCmd = Command(
    id="load file",
    title="Creates the link",
    syntax="load <file-path>",
    examples="load sample/faber-invitation.sovrin")

showLinkCmd = Command(
    id="show link",
    title="Shows link info in case of one matching link, otherwise shows all the matching link names",
    syntax="show link <link-name>",
    examples="show link faber")

connectToCmd = Command(
    id="connect",
    title="Lets you connect to the respective environment (test/live)",
    syntax="connect <env-name>",
    examples=["connect test", "connect live"])

disconnectCmd = Command(
    id="disconnect",
    title="Disconnects from currently connected environment",
    syntax="disconnect",
    examples="disconnect")

syncLinkCmd = Command(
    id="sync link",
    title="Synchronizes the link between the endpoints",
    syntax="sync link <link-name>",
    examples="sync link faber")

pingTargetCmd = Command(
    id="ping",
    title="Pings given target's endpoint",
    syntax="ping <target>",
    examples="ping faber")

showClaimCmd = Command(
    id="show claim",
    title="Shows given claim information",
    syntax="show claim <claim-name>",
    examples="show claim Transcript")

reqClaimCmd = Command(
    id="request claim",
    title="Request given claim",
    syntax="request claim <claim-name>",
    examples="request claim Transcript")

showClaimReqCmd = Command(
    id="show claim request",
    title="Shows given claim request",
    syntax="show claim request <claim-req-name>",
    examples="show claim request Job-Application")

acceptLinkCmd = Command(
    id="accept invitation",
    title="Accept invitation from given target",
    syntax="accept invitation from <target>",
    examples="accept invitation from Faber")

setAttrCmd = Command(
    id="set attributes",
    title="Sets given value to given attribute name",
    syntax="set <attr-name> to <attr-value>",
    examples="set first_name to Alice")

sendClaimCmd = Command(
    id="send claim",
    title="Sends given claim to given target",
    syntax="send claim <claim-name> to <target>",
    examples="send claim Job-Application to Acme Corp")

newIdentifierCmd = Command(
    id="new identifier",
    title="Creates new Identifier",
    syntax="new identifier [<identifier>|abbr|crypto] [with seed <seed>] [as <alias>]",
    examples=[
        "new identifier abbr",
        "new identifier 4QxzWk3ajdnEA37NdNU5Kt",
        "new identifier with seed aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "new identifier abbr with seed aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "new identifier 4QxzWk3ajdnEA37NdNU5Kt with seed aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"])