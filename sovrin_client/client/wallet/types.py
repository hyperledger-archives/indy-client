from typing import NamedTuple

AvailableClaim = NamedTuple("AvailableClaim", [("name", str),
                                               ("version", str),
                                               ("origin", str)])


# TODO _F_ Proof Requests need a nonce! Cannot borrow from Link Invitation.
class ProofRequest:
    def __init__(self, name, version, attributes, verifiableAttributes):
        self.name = name
        self.version = version
        self.attributes = attributes
        self.verifiableAttributes = verifiableAttributes
        # TODO _F_ need to add support for predicates on unrevealed attibutes

    @property
    def toDict(self):
        return {
            "name": self.name,
            "version": self.version,
            "attributes": self.attributes
        }

    @property
    def attributeValues(self):
        return \
            'Attributes:' + '\n    ' + \
            format("\n    ".join(
                ['{}: {}'.format(k, v)
                 for k, v in self.attributes.items()])) + '\n'

    @property
    def verifiableAttributeValues(self):
        return \
            'Verifiable Attributes:' + '\n    ' + \
            format("\n    ".join(
                ['{}'.format(v)
                 for v in self.verifiableAttributes])) + '\n'

    def __str__(self):
        fixedInfo = \
            'Status: Requested' + '\n' \
                                  'Name: ' + self.name + '\n' \
                                                         'Version: ' + self.version + '\n'

        return fixedInfo + self.attributeValues + self.verifiableAttributeValues
