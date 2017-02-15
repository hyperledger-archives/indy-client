from plenum.cli.HelpMsg import HelpMsg

sendNymHelpMsg = HelpMsg("send NYM",
                         "Adds given identifier to sovrin",
                         "send NYM dest=<target identifier> role=<role> [verkey=<ver-key>]",
                         "send NYM dest=BiCMHDqC5EjheFHumZX9nuAoVEp8xyuBgiRi5JcY5whi role=SPONSOR",
                         "send NYM dest=33A18XMqWqTzDpLHXLR5nT verkey=~Fem61Q5SnYhGVVHByQNxHj")

sendGetNymHelpMsg = HelpMsg("send GET_NYM",
                            "Get NYM from sovrin",
                            "send GET_NYM dest=<target identifier>",
                            "send GET_NYM dest=33A18XMqWqTzDpLHXLR5nT")

sendAttribHelpMsg = HelpMsg("send ATTRIB",
                            "Adds attributes to existing identifier",
                            "send ATTRIB dest=<target identifier> [raw={<json-data>}] [hash=<hashed-data>] [enc: <encrypted-data>]",
                            'send ATTRIB dest=33A18XMqWqTzDpLHXLR5nT raw={"endpoint": "127.0.0.1:5555"}')


sendNodeHelpMsg = HelpMsg("send NODE",
                          "Adds a node to the pool",
                          "send NODE dest=<target node identifier> data={<json-data>}",
                          'send NODE dest=87Ys5T2eZfau4AATsBZAYvqwvD8XL5xYCHgg2o1ffjqg data={node_ip: 127.0.0.1, node_port: 9701, client_ip: 127.0.0.1, client_port: 9702, alias: test01}')


sendPoolUpgHelpMsg = HelpMsg("send POOL_UPGRADE",
                             "Sends instructions to nodes to update themselves",
                             "send POOL_UPGRADE name=<name> version=<version> sha256=<sha256> action=<action> schedule=<schedule> timeout=<timeout>",
                             "send POOL_UPGRADE name=upgrade-01 "
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


sendSchemaMsg = HelpMsg("send SCHEMA",
                        "Adds schema to sovrin",
                        "send SCHEMA name=<schema-name> version=<version> type=<type> keys=<comma separated attributes>",
                        "send SCHEMA name=Degree version=1.0 type=CL keys=undergrad,last_name,first_name,birth_date,postgrad,expiry_date")

sendIssuerHelpMsg = HelpMsg("send ISSUER_KEY",
                            "Adds issuer keys for given schema",
                            "send ISSUER_KEY ref=<ref-no-of-SCHEMA-txn>",
                            "send ISSUER_KEY ref=10")

showFileHelpMsg = HelpMsg("show file",
                          "Shows content of given file",
                          "show <file-path>",
                          "show sample/faber-invitation.sovrin")

loadFileHelpMsg = HelpMsg("load file",
                          "Creates the link",
                          "load <file-path>",
                          "load sample/faber-invitation.sovrin")

showLinkHelpMsg = HelpMsg("show link",
                          "Shows link info in case of one matching link, otherwise shows all the matching link names",
                          "show link <link-name>",
                          "show link faber")

connectToHelpMsg = HelpMsg("connect",
                           "Lets you connect to the respective environment (test/live)",
                           "connect <env-name>",
                           "connect test", "connect live")

disconnectHelpMsg = HelpMsg("disconnect",
                            "Disconnects from currently connected environment",
                            "disconnect",
                            "disconnect")

syncLinkHelpMsg = HelpMsg("sync link",
                          "Synchronizes the link between the endpoints",
                          "sync link <link-name>",
                          "sync link faber")

pingTargetHelpMsg = HelpMsg("ping",
                            "Pings given target's endpoint",
                            "ping <target>",
                            "ping faber")

showClaimHelpMsg = HelpMsg("show claim",
                           "Shows given claim information",
                           "show claim <claim-name>",
                           "show claim Transcript")

reqClaimHelpMsg = HelpMsg("request claim",
                          "Request given claim",
                          "request claim <claim-name>",
                          "request claim Transcript")

showClaimReqHelpMsg = HelpMsg("show claim request",
                              "Shows given claim request",
                              "show claim request <claim-req-name>",
                              "show claim request Job-Application")

acceptLinkHelpMsg = HelpMsg("accept invitation",
                            "Accept invitation from given target",
                            "accept invitation from <target>",
                            "accept invitation from Faber")

setAttrHelpMsg = HelpMsg("set attributes",
                         "Sets given value to given attribute name",
                         "set <attr-name> to <attr-value>",
                         "set first_name to Alice")

sendClaimHelpMsg = HelpMsg("send claim",
                           "Sends given claim to given target",
                           "send claim <claim-name> to <target>",
                           "send claim Job-Application to Acme Corp")

newIdentifierHelpMsg = HelpMsg("new identifier",
                               "Creates new Identifier",
                               "new identifier [<identifier>|abbr|crypto] [with seed <seed>] [as <alias>]",
                               "new identifier abbr",
                               "new identifier 4QxzWk3ajdnEA37NdNU5Kt",
                               "new identifier with seed aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                               "new identifier abbr with seed aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                               "new identifier 4QxzWk3ajdnEA37NdNU5Kt with seed aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")