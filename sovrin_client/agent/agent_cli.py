from sovrin_client.cli.cli import SovrinCli


class AgentCli(SovrinCli):
    def __init__(self, name=None, agentCreator=None, *args, **kwargs):
        # assert agent is not None, 'agent is required'
        if name is not None:
            self.name = name
        # if 'name' in kwargs:
        #     self.name = kwargs['name']
        #     kwargs.pop('name')

        # if 'agentCreator' in kwargs:
        #     kwargs.pop('agentCreator')

        super().__init__(*args, **kwargs)

        self._activeWallet = None

        if 'agent' in kwargs:
            self.agent = kwargs['agent']


        # self.registerAgentListeners(self._agent)
        # self._activeWallet = self._agent.wallet
        # self.wallets[self._agent.wallet.name] = self._agent.wallet


        # looper = kwargs.get()
        # if looper is not None and self._agent is not None:
        #     looper.add(self._agent)

    # @property
    # def agent(self):
    #     return super(SovrinCli, self).agent()

    @SovrinCli.agent.setter
    def agent(self, agent):
        # this is hackish but I could not find a more elegant way
        # was trying to do 'super(SovrinCli, self).agent = agent'
        # but that did not work
        super(AgentCli, type(self)).agent.fset(self, agent)

        if self._agent is not None:
            self._activeWallet = self._agent.wallet
            self.wallets[self._agent.wallet.name] = self._agent.wallet
            self.name = agent.name

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

    def getAllSubDirNamesForKeyrings(self):
        return ["issuer"]

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
