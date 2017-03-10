from sovrin_client.agent.endpoint import Endpoint


class AgentNet:
    """
    Mixin for Agents to encapsulate the network interface to communicate with
    other agents.
    """
    def __init__(self, name, port, msgHandler, basedirpath=None):
        if port:
            self.endpoint = Endpoint(port=port,
                                     msgHandler=msgHandler,
                                     name=name,
                                     basedirpath=basedirpath)
        else:
            self.endpoint = None
