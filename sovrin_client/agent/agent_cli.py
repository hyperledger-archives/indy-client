from sovrin_client.cli.cli import SovrinCli


class AgentCli(SovrinCli):
    def __init__(self, name, agentCreator=None, *args, **kwargs):
        assert agentCreator is not None, 'agentCreator is required'
        self._agentCreator = agentCreator
        self.name = name
        self._activeWallet = None
        super().__init__(*args, **kwargs)

    @property
    def agent(self):
        if self._agent is None:
            self._agent = self._agentCreator()
            self.registerAgentListeners(self._agent)
            self.looper.add(self._agent)
        return self._agent

    @property
    def activeWallet(self):
        return self.agent._wallet
    
    @activeWallet.setter
    def activeWallet(self, wallet):
        pass
