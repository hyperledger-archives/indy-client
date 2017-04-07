import jsonpickle

from anoncreds.protocol.types import PublicKey, RevocationPublicKey, SecretKey, \
    RevocationSecretKey, AccumulatorSecretKey
from anoncreds.protocol.utils import toDictWithStrValues, fromDictWithStrValues

OBJECTVALUE = 'py/integer-element'


class CommonIntegerElementHandler(jsonpickle.handlers.BaseHandler):
    def flatten(self, obj, data):
        data[OBJECTVALUE] = toDictWithStrValues(obj)
        return data


class PublicKeyHandler(CommonIntegerElementHandler):
    def restore(self, obj):
        origObj = fromDictWithStrValues(obj[OBJECTVALUE])
        return PublicKey(origObj.get("N"), origObj.get("Rms"),
                       origObj.get("Rctxt"), origObj.get("R"),
                       origObj.get("S"), origObj.get("Z"), origObj.get("seqId"))


class RevocationPublicKeyHandler(CommonIntegerElementHandler):
    def restore(self, obj):
        origObj = fromDictWithStrValues(obj[OBJECTVALUE])
        return RevocationPublicKey(
            origObj.get("qr"), origObj.get("g"), origObj.get("h"),
            origObj.get("h0"), origObj.get("h1"), origObj.get("h2"),
            origObj.get("htilde"), origObj.get("u"), origObj.get("pk"),
            origObj.get("y"), origObj.get("x"), origObj.get("seqId")
        )


class SecretKeyHandler(CommonIntegerElementHandler):
    def restore(self, obj):
        origObj = fromDictWithStrValues(obj[OBJECTVALUE])
        return SecretKey(origObj.get("pPrime"), origObj.get("qPrime"))


class RevocationSecretKeyHandler(CommonIntegerElementHandler):
    def restore(self, obj):
        origObj = fromDictWithStrValues(obj[OBJECTVALUE])
        return RevocationSecretKey(origObj.get("x"), origObj.get("sk"))


class AccumulatorSecretKeyHandler(CommonIntegerElementHandler):
    def restore(self, obj):
        origObj = fromDictWithStrValues(obj[OBJECTVALUE])
        return AccumulatorSecretKey(origObj.get("gamma"))


def setUpJsonpickle():
    customHandlers = [
        (PublicKey, PublicKeyHandler),
        (RevocationPublicKey, RevocationPublicKeyHandler),
        (SecretKey, SecretKeyHandler),
        (RevocationSecretKey, RevocationSecretKeyHandler),
        (AccumulatorSecretKey, AccumulatorSecretKeyHandler)
    ]
    for cls, handler in customHandlers:
        jsonpickle.handlers.register(cls, handler, base=True)
