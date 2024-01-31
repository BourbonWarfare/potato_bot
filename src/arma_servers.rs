use crate::{SERVERLIST, SOCKET};
use futures_util::FutureExt;
use rust_socketio::Payload;
use serde::{Deserialize, Serialize};
use serde_json::json;
use tokio::time::Duration;
use tracing::{info, instrument};

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct A3ServerConfig {
    pub name: String,
    pub name_pretty: String,
    pub game_port: String,
    pub hc: String,
    pub location: String,
    pub ip: String,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct ServerList {
    list: Vec<A3ServerConfig>,
}

#[instrument]
pub async fn get_serverlist() {
    let ack_callback = |data: Payload, _: rust_socketio::asynchronous::Client| {
        async move {
            let server_list: ServerList = match data {
                Payload::String(string) => serde_json::from_str(string.as_str()).unwrap(),
                _ => panic!("Invalid payload type"),
            };
            info!("server_list: {:?}", server_list);
            let _ = SERVERLIST.set(server_list.list);
        }
        .boxed()
    };
    let socket = SOCKET.get().unwrap();
    let output = socket
        .emit_with_ack(
            "serverlist",
            json!({"caller": "potato_bot",}),
            Duration::from_secs(2),
            ack_callback,
        )
        .await
        .expect("unable to send serverlist request");
    info!("output: {:?}", output);
}
