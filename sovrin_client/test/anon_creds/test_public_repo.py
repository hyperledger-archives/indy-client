import sys

import pytest
from anoncreds.protocol.issuer import Issuer
from anoncreds.protocol.repo.attributes_repo import AttributeRepoInMemory
from anoncreds.protocol.types import Schema, ID
from anoncreds.protocol.wallet.issuer_wallet import IssuerWalletInMemory
from stp_core.common.log import getlogger

from sovrin_client.anon_creds.sovrin_public_repo import SovrinPublicRepo
from sovrin_client.test.anon_creds.conftest import GVT


logger = getlogger()


@pytest.fixture(scope="module")
def publicRepo(steward, stewardWallet):
    return SovrinPublicRepo(steward, stewardWallet)


@pytest.fixture(scope="module")
def issuerGvt(publicRepo):
    return Issuer(IssuerWalletInMemory('issuer1', publicRepo),
                  AttributeRepoInMemory())


@pytest.fixture(scope="module")
def schemaDefGvt(stewardWallet):
    return Schema('GVT', '1.0', GVT.attribNames(), 'CL',
                           stewardWallet.defaultId)


@pytest.fixture(scope="module")
def submittedSchemaDefGvt(publicRepo, schemaDefGvt, looper):
    return looper.run(publicRepo.submitSchema(schemaDefGvt))


@pytest.fixture(scope="module")
def submittedSchemaDefGvtID(submittedSchemaDefGvt):
    return ID(schemaKey=submittedSchemaDefGvt.getKey(),
              schemaId=submittedSchemaDefGvt.seqId)


@pytest.fixture(scope="module")
def publicSecretKey(submittedSchemaDefGvtID, issuerGvt, primes1, looper):
    return looper.run(
        issuerGvt._primaryIssuer.genKeys(submittedSchemaDefGvtID, **primes1))


@pytest.fixture(scope="module")
def publicSecretRevocationKey(issuerGvt, looper):
    return looper.run(issuerGvt._nonRevocationIssuer.genRevocationKeys())


@pytest.fixture(scope="module")
def publicKey(publicSecretKey):
    return publicSecretKey[0]


@pytest.fixture(scope="module")
def publicRevocationKey(publicSecretRevocationKey):
    return publicSecretRevocationKey[0]


@pytest.fixture(scope="module")
def submittedPublicKeys(submittedSchemaDefGvtID, publicRepo, publicSecretKey,
                        publicSecretRevocationKey, looper):
    pk, sk = publicSecretKey
    pkR, skR = publicSecretRevocationKey
    return looper.run(
        publicRepo.submitPublicKeys(id=submittedSchemaDefGvtID, pk=pk, pkR=pkR))


@pytest.fixture(scope="module")
def submittedPublicKey(submittedPublicKeys):
    return submittedPublicKeys[0]


@pytest.fixture(scope="module")
def submittedPublicRevocationKey(submittedPublicKeys):
    return submittedPublicKeys[1]


def testSubmitSchema(submittedSchemaDefGvt, schemaDefGvt):
    assert submittedSchemaDefGvt
    assert submittedSchemaDefGvt.seqId
    # initial schema didn't have seqNo
    submittedSchemaDefGvt = submittedSchemaDefGvt._replace(seqId=None)
    assert submittedSchemaDefGvt == schemaDefGvt


def testGetSchema(submittedSchemaDefGvt, publicRepo, looper):
    schema = looper.run(
        publicRepo.getSchema(ID(schemaKey=submittedSchemaDefGvt.getKey())))
    assert schema == submittedSchemaDefGvt


def testSubmitPublicKey(submittedPublicKeys):
    assert submittedPublicKeys


def testGetPrimaryPublicKey(submittedSchemaDefGvtID, submittedPublicKey,
                            publicRepo, looper):
    pk = looper.run(publicRepo.getPublicKey(id=submittedSchemaDefGvtID))
    assert pk == submittedPublicKey


def testGetRevocationPublicKey(submittedSchemaDefGvtID,
                               submittedPublicRevocationKey,
                               publicRepo, looper):
    pk = looper.run(
        publicRepo.getPublicKeyRevocation(id=submittedSchemaDefGvtID))

    if sys.platform == 'win32':
        assert pk
        logger.warning("Gotten public revocation key is not verified "
                       "on Windows for matching against submitted public "
                       "revocation key since they are different on Windows "
                       "due to an issue in charm-crypto package.")
    else:
        assert pk == submittedPublicRevocationKey
