use crate::CacheAndHttp;
use axum::Json;
use log::error;
use log::info;
use serde::{Deserialize, Serialize};
use serde_json::Value;

use serenity::model::id::ChannelId;

#[derive(Serialize, Deserialize)]
pub struct Message {
    target: String,
    message: String,
    title: String,
}

pub async fn message(Json(payload): Json<Value>) {
    info!("Received message request: {:?}", payload);

    let request_contents: Message = serde_json::from_value(payload).unwrap();

    let channel_id = ChannelId::from(request_contents.target.parse::<u64>().unwrap());

    let response = channel_id
        .send_message(&CacheAndHttp::get().http, |m| {
            m.content(request_contents.message)
        })
        .await;

    match response {
        Ok(_) => {
            info!("Message sent successfully");
        }
        Err(_) => {
            error!("Message failed to send");
        }
    };
}

pub async fn embed(Json(payload): Json<Value>) {
    info!("Received embed request: {:?}", payload);

    let request_contents: Message = serde_json::from_value(payload).unwrap();

    let channel_id = ChannelId::from(request_contents.target.parse::<u64>().unwrap());

    let response = channel_id
        .send_message(&CacheAndHttp::get().http, |m| {
            m.embed(|e| {
                e.title(request_contents.title)
                    .description(request_contents.message)
            })
        })
        .await;

    match response {
        Ok(_) => {
            info!("Embed sent successfully");
        }
        Err(_) => {
            error!("Message failed to send");
        }
    };
}
