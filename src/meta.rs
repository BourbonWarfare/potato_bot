use crate::prelude::*;

lazy_static! {
    pub static ref SOCKET: OnceCell<rust_socketio::asynchronous::Client> = OnceCell::new();
    pub static ref CONFIG: config::Config = config::get();
}

pub fn init() {
    // Make sure that all lazy_statics are initialzied
    lazy_static::initialize(&CONFIG);
    lazy_static::initialize(&SOCKET);
}
