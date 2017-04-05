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
            self._activeWallet = self._agent.wallet
            self.wallets[self._agent.wallet.name] = self._agent.wallet
        return self._agent

    @property
    def actions(self):
        if not self._actions:
            self._actions = [self._simpleAction, self._helpAction,
                             self._listIdsAction, self._changePrompt,
                             self._listKeyringsAction, self._showFile,
                             self._showLink, self._pingTarget,
                             self._listLinks, self._sendProofRequest]
        return self._actions

    def getKeyringsBaseDir(self):
        return self.agent.getContextDir()

    def getContextBasedKeyringsBaseDir(self):
        return self.agent.getContextDir()

    def getAllEnvDirNamesForKeyrings(self):
        return []

    def getTopComdMappingKeysForHelp(self):
        return ['helpAction']

    def getComdMappingKeysToNotShowInHelp(self):
        allowedCmds = [func.__name__.replace("_","") for func in self.actions ]
        return {k: v for (k, v) in
                self.cmdHandlerToCmdMappings().items() if k not in allowedCmds}

    def getBottomComdMappingKeysForHelp(self):
        return ['licenseAction', 'exitAction']

    def restoreLastActiveWallet(self):
        pass

    def _saveActiveWallet(self):
        pass

    def printSuggestion(self, msgs):
        self.print("\n")
        # TODO: as of now we are not printing the suggestion (msg)
        # because, those suggestion may not be intented or may not work
        # correctly for agents, so when such requirement will come,
        # we can look this again.

    @property
    def activeWallet(self):
        return self.agent._wallet
    
    @activeWallet.setter
    def activeWallet(self, wallet):
        pass
