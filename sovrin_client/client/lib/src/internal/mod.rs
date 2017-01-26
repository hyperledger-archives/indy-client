/// Allow state to be owned inside this object. C-callable functions exposed by this library
/// are not object-oriented, so we create a static list of these objects and then refer to them
/// by id as the first parameter of each function. This allows us to look up state without
/// requiring the consumer of the lib to manage it in an object that crosses the lib boundary.
pub struct Client {

}

impl Client {
    pub fn new(host_and_port: &str) -> Client {
        Client {}
    }
}

// this next function is a stub where we need to call libsodium to wrap messages, unless we decide
// to use CurveCP instead.

// Example of how to link to a system library. Libsodium will follow this pattern.
/*
#[link(name = "snappy")]
extern {
    fn snappy_compress(input: *const u8,
                       input_length: size_t,
                       compressed: *mut u8,
                       compressed_length: *mut size_t) -> c_int;
}
*/

/// Use public key cryptography to encrypt a message for a particular recipient.
pub fn encrypt_msg(msg: &[u8], src_priv_key: &[u8], tgt_pub_key: &[u8]) {
/*
    Sample C code from libsodium:

    #define MESSAGE (const unsigned char *) "test"
    #define MESSAGE_LEN 4
    #define CIPHERTEXT_LEN (crypto_box_MACBYTES + MESSAGE_LEN)

    unsigned char alice_publickey[crypto_box_PUBLICKEYBYTES];
    unsigned char alice_secretkey[crypto_box_SECRETKEYBYTES];
    crypto_box_keypair(alice_publickey, alice_secretkey);

    unsigned char bob_publickey[crypto_box_PUBLICKEYBYTES];
    unsigned char bob_secretkey[crypto_box_SECRETKEYBYTES];
    crypto_box_keypair(bob_publickey, bob_secretkey);

    unsigned char nonce[crypto_box_NONCEBYTES];
    unsigned char ciphertext[CIPHERTEXT_LEN];
    randombytes_buf(nonce, sizeof nonce);
    if (crypto_box_easy(ciphertext, MESSAGE, MESSAGE_LEN, nonce,
    bob_publickey, alice_secretkey) != 0) {
    /* error */
    }

    unsigned char decrypted[MESSAGE_LEN];
    if (crypto_box_open_easy(decrypted, ciphertext, CIPHERTEXT_LEN, nonce,
    alice_publickey, bob_secretkey) != 0) {
    /* message for Bob pretending to be from Alice has been forged! */
    }
*/
}

