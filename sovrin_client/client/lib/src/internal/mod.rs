extern crate libc;


use libc::{c_int, size_t, c_char};
use std::ffi::{CStr, CString};
use std::panic;
use std::ptr;


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

// Temporary measure until we can maintain a mutexed list of clients.
static THE_ONLY_CLIENT_RIGHT_NOW: Client = Client {};

pub fn get_client_from_id(client_id: i32) -> Option<&'static Client> {
    // Right now, this next line is a useless optimization. But when we have a client array,
    // it will save a mutex on error cases.
    if client_id < 0 { return None }
    if client_id == 0 { return Some(&THE_ONLY_CLIENT_RIGHT_NOW) }
    None
}

/// Rust's ptr::null() returns a const null ptr; this function gives us a null, mutable char *
/// in a single step.
pub fn null_ptr_as_c_str() -> *mut c_char {
    let p: *const c_char = ptr::null();
    p as *mut c_char
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


/// Convert a c-style string into a Rust-style String, owned on the Rust side of the lib boundary.
/// If the input value is a null ptr, contains invalid utf-8, or has other panic-worthy problems,
/// return None. An empty string (a C-style array where the first byte is null) is considered
/// valid.
pub fn string_from_c_ptr(cstr: *const c_char) -> Option<String> {
    if !cstr.is_null() {

        // Catch any panics that may happen inside Rust over the next few lines of logic, so we don't
        // attempt to propagate the panics across a lib boundary; that would yield undefined behavior.
        // This mechanis is not foolproof--some panics in Rust abort a process instead of unwinding
        // the stack. It is not intended to work like a generic try...catch. But it does make our
        // library more robust. See http://bit.ly/2koEXss.
        let result = panic::catch_unwind(|| {

            // Now wrap arg in a CStr, which gives a Rust-style object interface to the ptr.
            // This is unsafe for several reasons; the ones we can't protect against are bogus ptrs
            // or ptrs to data that isn't null-terminated. In such cases, the next line will cause an
            // access violation because the current impl of from_ptr() attempts to find the null
            // terminator. This behavior may change; it is an accident rather than a contract of the
            // from_ptr method.
            let cstr = unsafe { CStr::from_ptr(cstr) };

            // Now, attempt to get a reference to the string slice (&str). This will only succeed if
            // the text is valid utf8; otherwise an error is returned.
            let x = cstr.to_str();
            if x.is_err() { return Err(x) }

            // Convert Result<> to &str. We know this will succeed, if we got this far.
            let slice = x.unwrap();

            // We have a lifetime/ownership challenge. The CStr that provides the &str is about to
            // go out of scope as this closure exits. Although the underlying memory is not going
            // to be harvested (because CStr doesn't do that), the &str becomes invalid. So we
            // have to take ownership (make a copy) of the buffer to keep our value outside the
            // closure's scope. We do this by returning a String instead of a CStr.
            Ok(slice.to_string())
        });

        // See what our closure gave us. If a valid value, return it; otherwise, return None.
        if result.is_ok() {
            return Some(result.unwrap().unwrap());
        }
    }
    None
}


macro_rules! check_client {
    ($x:ident, $e:expr) => {
        let client = get_client_from_id($x);
        if client.is_none() { return $e }
    }
}


macro_rules! check_client_with_null_as_error {
    ($x:ident) => { check_client!($x, null_ptr_as_c_str()) }
}


macro_rules! check_client_with_num_as_error {
    ($x:ident) => { check_client!($x, BAD_FIRST_ARG) }
}

macro_rules! check_useful_str {
    ($x:ident, $e:expr) => {
        let $x = match string_from_c_ptr($x) {
            None => return $e,
            Some(val) => val
        };
        if $x.is_empty() { return $e }
    }
}

macro_rules! check_useful_str_with_null_as_error {
    ($x:ident) => { check_useful_str!($x, null_ptr_as_c_str()) }
}


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

