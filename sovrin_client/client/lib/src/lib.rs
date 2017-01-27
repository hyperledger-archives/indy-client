#![crate_type = "lib"]

// Jan 25, 2017: Turn off certain warnings while we're experimenting with techniques, features, and
// tests. For the time being, we don't want the noise. Remove these attributes when we are ready to
// be serious about implementation; we do NOT want to ignore these for more than a few days.
#![allow(dead_code)]
#![allow(unused_variables)]
#![allow(unused_imports)]

// To make it easy to use C data types, import the libc crate.
extern crate libc;
use libc::{c_int, size_t};

mod internal;
mod tests;


/// Create a client handle that manages state such as a connection to the ledger, propagated errors,
/// and so forth. All calls to the ledger require a client as context.
///
/// An individual client is NOT inherently threadsafe; callers should ensure either that a client
/// is only accessed from a single thread, or that it is mutexed appropriately. Clients are cheap
/// and easy to create, so creating one per thread is perfectly reasonable. You can have as many
/// clients working in parallel as you like.
///
/// @return the id of the client on success (in which case the number will be non-negative),
///     or an error code on failure (in which case the number will be negative).
pub extern fn init_client(host_and_port: &str) -> i32 {
    0
}

/// Release a client to free its resources. This call is idempotent.
pub extern fn release_client(client_id: i32) -> i32 {
    0
}


/// Write a new DID to the ledger, or update an existing DID's attributes.
/// @param dest: the DID that will be created or modified--or a DID alias.
/// @param verkey: the verkey for the new DID. Optional; if empty/null, defaults to same value as dest.
/// @param xref: if dest is an alias, this is the DID it refers to. Otherwise, ignored.
/// @param data: Optional. The alias for the DID.
/// @param role: Optional. One of "USER", "SPONSOR", "STEWARD", "TRUSTEE", or null/empty.
///     Assigns a role to the DID, or removes all roles (and thus all privileges for writing) if
///     null empty. (The latter can only be one by a trustee.)
/// Only a steward can create new sponsors; only other trustees can create a new trustee.
#[no_mangle]
pub extern fn set_did(client_id: i32, dest: &str, verkey: &str, xref: &str, data: &str, role: &str) -> i32 {
    0
}

/// Look up information about a DID.
#[no_mangle]
pub extern fn get_did(client_id: i32, did: &str) {
}

/// Set an arbitrary attribute for a DID.
/// @param hash: the sha256 hash of the attribute value. Required.
/// @param raw: the raw bytes of the attribute value. Optional and often omitted--in which case
///     what's recorded on the ledger is just proof of existence, with the value stored elsewhere.
///     This param is used to record public data such as the mailing address of a government
///     office; it should be null for data that has any privacy constraints.
/// @param enc: the encrypted bytes of the attribute value.
#[no_mangle]
pub extern fn set_attr(client_id: i32, dest: &str, hash: &str, raw: &str, enc: &str) {
}

/// Get an arbitrary attribute for a DID.
#[no_mangle]
pub extern fn get_attr(client_id: i32) {
}

/// Define a schema on the ledger (e.g., for a claim type or proof type).
#[no_mangle]
pub extern fn set_schema(client_id: i32) {
}

/// Retrieve the definition for a particular schema, as stored on the ledger.
#[no_mangle]
pub extern fn get_schema(client_id: i32) {
}

#[no_mangle]
pub extern fn set_issuer_key(client_id: i32) {
}

#[no_mangle]
pub extern fn get_issuer_key(client_id: i32) {
}

// TODO: NODE, PROPOSE, CANCEL, EXECUTE, VOTE, CONFIG, DECRY
