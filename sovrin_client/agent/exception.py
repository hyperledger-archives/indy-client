
class NonceNotFound(RuntimeError):
    pass


class SignatureRejected(RuntimeError):
    pass


class AgentBootstrapFailed(RuntimeError):
    pass
