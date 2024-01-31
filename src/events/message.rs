use axum::Json;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::io::Error;
use tracing::{error, info};

use serenity::{
    builder::{CreateEmbed, CreateMessage},
    model::id::ChannelId,
};

use crate::bots::BotCache;

#[derive(Serialize, Deserialize)]
pub struct Message {
    target: String,
    message: String,
    title: String,
}

fn get_target(target: String) -> Result<u64, Error> {
    let target_uid = match target.as_str() {
        "arma" => std::env::var("ARMA_GENERAL_CHANNEL_ID")
            .expect("ARMA_GENERAL_CHANNEL_ID not found in env"),
        "member" => std::env::var("MEMBER_CHANNEL_ID").expect("MEMBER_CHANNEL_ID not found in env"),
        "staff" => std::env::var("STAFF_CHANNEL_ID").expect("STAFF_CHANNEL_ID not found in env"),
        "admin" => std::env::var("ADMIN_CHANNEL_ID").expect("ADMIN_CHANNEL_ID not found in env"),
        "tech" => {
            std::env::var("TECH_STAFF_CHANNEL_ID").expect("TECH_STAFF_CHANNEL_ID not found in env")
        }
        "recruit" => std::env::var("RECRUITMENT_CHANNEL_ID")
            .expect("RECRUITMENT_CHANNEL_ID not found in env"),
        "bot" => {
            std::env::var("BOT_SPAM_CHANNEL_ID").expect("BOT_SPAM_CHANNEL_ID not found in env")
        }
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
        .send_message(
            &BotCache::get(),
            CreateMessage::new().content(request_contents.message),
        )
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
        .send_message(&BotCache::get(), {
            CreateMessage::new().embed(
                CreateEmbed::new()
                    .title(request_contents.title)
                    .description(request_contents.message),
            )
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
