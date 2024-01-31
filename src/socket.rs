use crate::SOCKET;
use rust_socketio::asynchronous::ClientBuilder;
use tracing::error;
use tracing::info;

pub async fn init() {
    info!("Initializing socketio client");
    let socket = ClientBuilder::new("http://127.0.0.1:8082/")
        .connect()
        .await
        .expect("Unable to connect to socketio server");

    let _ = SOCKET.set(socket);

    let _ = SOCKET
        .get()
        .expect("unable to get valid socket")
        .emit("join", "")
        .await;
}
