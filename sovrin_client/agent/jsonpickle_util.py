import jsonpickle

from anoncreds.protocol.types import PublicKey, RevocationPublicKey, \
    SecretKey, RevocationSecretKey, AccumulatorSecretKey
from anoncreds.protocol.utils import toDictWithStrValues, fromDictWithStrValues

DATA_KEY = 'py/integer-element'


class CommonIntegerElementHandler(jsonpickle.handlers.BaseHandler):
    def flatten(self, obj, data):
        data[DATA_KEY] = toDictWithStrValues(obj)
        return data

    def restore(self, obj):
        dict = fromDictWithStrValues(obj[DATA_KEY])
        return self._restore(dict)

    def _restore(self, dict):
        raise NotImplemented


class PublicKeyHandler(CommonIntegerElementHandler):
    def _restore(self, dict):
        return PublicKey(dict.get("N"), dict.get("Rms"),
                         dict.get("Rctxt"), dict.get("R"),
                         dict.get("S"), dict.get("Z"), dict.get("seqId"))


class RevocationPublicKeyHandler(CommonIntegerElementHandler):
    def _restore(self, dict):
        return RevocationPublicKey(
            dict.get("qr"), dict.get("g"), dict.get("h"),
            dict.get("h0"), dict.get("h1"), dict.get("h2"),
            dict.get("htilde"), dict.get("u"), dict.get("pk"),
            dict.get("y"), dict.get("x"), dict.get("seqId")
        )


class SecretKeyHandler(CommonIntegerElementHandler):
    def _restore(self, dict):
        return SecretKey(dict.get("pPrime"), dict.get("qPrime"))


class RevocationSecretKeyHandler(CommonIntegerElementHandler):
    def _restore(self, dict):
        return RevocationSecretKey(dict.get("x"), dict.get("sk"))


class AccumulatorSecretKeyHandler(CommonIntegerElementHandler):
    def _restore(self, dict):
        return AccumulatorSecretKey(dict.get("gamma"))


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
