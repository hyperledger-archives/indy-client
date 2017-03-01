from sovrin_client.agent.endpoint import Endpoint, ZEndpoint


class AgentNet:
    """
    Mixin for Agents to encapsulate the network interface to communicate with
    other agents.
    """
    def __init__(self, name, port, basedirpath, msgHandler, config,
                 endpointArgs=None):
        if port:
            if config.UseZStack:
                endpointArgs = endpointArgs or {}
                seed = endpointArgs.get('seed')
                onlyListener = endpointArgs.get('onlyListener', False)
                self.endpoint = ZEndpoint(port=port,
                                          msgHandler=msgHandler,
                                          name=name,
                                          basedirpath=basedirpath,
                                          seed=seed,
                                          onlyListener=onlyListener)
            else:
                self.endpoint = Endpoint(port=port,
                                         msgHandler=msgHandler,
                                         name=name,
                                         basedirpath=basedirpath)
        else:
            self.endpoint = None
