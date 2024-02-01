use crate::{events, SOCKET};
use futures_util::FutureExt;
use rust_socketio::{asynchronous::ClientBuilder, Payload};
use serde_json::{json, Value};
use tracing::info;

pub async fn init() {
    info!("Initializing socketio client");
    let socket = ClientBuilder::new("http://127.0.0.1:8082")
        .on("test", |args, _| {
            async move {
                info!("test message: {:?}", args);
            }
            .boxed()
        })
        .on(
            "send_message",
            |args: Payload, socket: rust_socketio::asynchronous::Client| {
                async move {
                    let response = match args {
                        Payload::String(string) => events::message::message(string).await,
                        _ => panic!("Invalid payload type"),
                    };
                    let _ = socket.emit("bot_result", json!(response)).await;
                }
                .boxed()
            },
        )
        .on(
            "send_embed",
            |args: Payload, socket: rust_socketio::asynchronous::Client| {
                async move {
                    let response = match args {
                        Payload::String(string) => events::message::embed(string).await,
                        _ => panic!("Invalid payload type"),
                    };
                    let _ = socket.emit("bot_result", json!(response)).await;
                }
                .boxed()
            },
        )
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
