use crate::prelude::*;

pub async fn init() {
    info!("Initializing socketio client");
    let socket = ClientBuilder::new("http://127.0.0.1:8082")
        .on("test", |args, _| {
            async move {
                info!("test message: {:?}", args);
            }
            .boxed()
        })
        .on("result", |args, _| {
            async move {
                info!("Result from PSM: {:?}", args);
            }
            .boxed()
        })
        .on(rust_socketio::Event::Error, |err, _| {
            async move {
                error!("Client encountered error: {:#?}", err);
            }
            .boxed()
        })
        .on(rust_socketio::Event::Connect, |_, _| {
            async move {
                error!("Client connected");
            }
            .boxed()
        })
        .on("send_message", |args: Payload, socket: SioClient| {
            async move {
                let response = match args {
                    Payload::Text(string) => Ok(events::message::message(string).await.unwrap()),
                    _ => Err(PotatoError::Socket(SocketError::InvalidPayload())),
                };
                let _ = socket.emit("bot_result", json!(response.unwrap())).await;
            }
            .boxed()
        })
        .on("send_embed", |args: Payload, socket: SioClient| {
            async move {
                let response = match args {
                    Payload::Text(string) => Ok(events::message::embed(string).await.unwrap()),
                    _ => Err(PotatoError::Socket(SocketError::InvalidPayload())),
                };
                let _ = socket.emit("bot_result", json!(response.unwrap())).await;
            }
            .boxed()
        })
        .on(
            "update_arma_servers_response",
            |args: Payload, socket: SioClient| {
                async move {
                    let response = match args {
                        Payload::Text(string) => Ok(events::message::embed(string).await.unwrap()),
                        _ => Err(PotatoError::Socket(SocketError::InvalidPayload())),
                    };
                    let _ = socket.emit("bot_result", json!(response.unwrap())).await;
                }
                .boxed()
            },
        )
        .on(
            "update_arma_mods_response",
            |args: Payload, socket: SioClient| {
                async move {
                    let response = match args {
                        Payload::Text(string) => Ok(events::message::embed(string).await.unwrap()),
                        _ => Err(PotatoError::Socket(SocketError::InvalidPayload())),
                    };
                    let _ = socket.emit("bot_result", json!(response.unwrap())).await;
                }
                .boxed()
            },
        )
        .on(
            "arma_server_manage_response",
            |args: Payload, socket: SioClient| {
                async move {
                    let response = match args {
                        Payload::Text(string) => Ok(events::message::embed(string).await.unwrap()),
                        _ => Err(PotatoError::Socket(SocketError::InvalidPayload())),
                    };
                    let _ = socket.emit("bot_result", json!(response.unwrap())).await;
                }
                .boxed()
            },
        )
        .on("mod_update_message", |args: Payload, socket: SioClient| {
            async move {
                let response = match args {
                    Payload::Text(string) => {
                        Ok(events::message::mod_update_message(string).await.unwrap())
                    }
                    _ => Err(PotatoError::Socket(SocketError::InvalidPayload())),
                };
                let _ = socket.emit("bot_result", json!(response.unwrap())).await;
            }
            .boxed()
        })
        .on(
            "scheduled_session_message",
            |args: Payload, socket: SioClient| {
                async move {
                    let response = match args {
                        Payload::Text(string) => {
                            Ok(events::message::scheduled_session_message(string)
                                .await
                                .unwrap())
                        }
                        _ => Err(PotatoError::Socket(SocketError::InvalidPayload())),
                    };
                    let _ = socket.emit("bot_result", json!(response.unwrap())).await;
                }
                .boxed()
            },
        )
        .reconnect_on_disconnect(true)
        .connect()
        .await
        .expect("Unable to connect to socketio server");

    let _ = SOCKET_CLIENT.set(socket);
}
