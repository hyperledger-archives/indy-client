from plenum.common.crypto import ed25519PkToCurve25519
from plenum.common.util import friendlyToRaw, rawToFriendly


def friendlyVerkeyToPubkey(verkey):
    vkRaw = friendlyToRaw(verkey)
    pkraw = ed25519PkToCurve25519(vkRaw)
    return rawToFriendly(pkraw)
