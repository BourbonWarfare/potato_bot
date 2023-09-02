use crate::CacheAndHttp;
use axum::Json;
use log::error;
use log::info;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::io::Error;

use serenity::model::id::ChannelId;

#[derive(Serialize, Deserialize)]
pub struct Message {
    target: String,
    message: String,
    title: String,
}

fn get_target(target: String) -> Result<u64, Error> {
    let target_uid = match target.as_str() {
        "arma" => std::env::var("ARMA_GENERAL").expect("Did not find channel id in env"),
        "member" => std::env::var("MEMBER_CHANNEL").expect("Did not find channel id in env"),
        "staff" => std::env::var("STAFF_CHANNEL").expect("Did not find channel id in env"),
        "admin" => std::env::var("ADMIN_CHANNEL").expect("Did not find channel id in env"),
        "tech" => std::env::var("TECH_STAFF_CHANNEL").expect("Did not find channel id in env"),
        "recruit" => std::env::var("RECRUITMENT_CHANNEL").expect("Did not find channel id in env"),
        "bot" => std::env::var("BOT_SPAM_CHANNEL").expect("Did not find channel id in env"),
        _ => {
            error!("Not a valid target");
            "".to_string()
        }
    };
    let target_u64 = target_uid
        .parse::<u64>()
        .expect("Unable to parse the target");
    Ok(target_u64)
}

pub async fn message(Json(payload): Json<Value>) {
    info!("Received message request: {:?}", payload);

    let request_contents: Message = serde_json::from_value(payload).unwrap();

    let target = get_target(request_contents.target).expect("Unable to get valid target channel");

    let channel_id = ChannelId::from(target);

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

    let target = get_target(request_contents.target).expect("Unable to get valid target channel");

    let channel_id = ChannelId::from(target);

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
