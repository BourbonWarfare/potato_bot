use std::io::Error;
use tracing::{error, info};

use serenity::{
    builder::{CreateAttachment, CreateEmbed, CreateMessage},
    model::id::ChannelId,
};

use crate::http::BotCache;

#[derive(Debug, serde::Deserialize, serde::Serialize)]
struct Message {
    message: String,
    channel: String,
    title: Option<String>,
    attachment: Option<String>,
}

fn get_target(target: String) -> Result<u64, Error> {
    let target_uid = match target.as_str() {
        "arma" => std::env::var("ARMA_GENERAL_CHANNEL_ID")
            .expect("ARMA_GENERAL_CHANNEL_ID not found in env"),
        "member" => std::env::var("MEMBER_CHANNEL_ID").expect("MEMBER_CHANNEL_ID not found in env"),
        "staff" => std::env::var("STAFF_CHANNEL_ID").expect("STAFF_CHANNEL_ID not found in env"),
        "admin" => std::env::var("ADMIN_CHANNEL_ID").expect("ADMIN_CHANNEL_ID not found in env"),
        "tech" => std::env::var("TECH_CHANNEL_ID").expect("TECH_STAFF_CHANNEL_ID not found in env"),
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

pub async fn message(payload: String) -> String {
    info!("Received message request: {:?}", payload);

    let request_contents: Message =
        serde_json::from_str(payload.as_str()).expect("Unable to parse message");

    let target = get_target(request_contents.channel).expect("Unable to get valid target channel");

    let channel_id = ChannelId::from(target);

    let response = channel_id
        .send_message(
            &BotCache::get(),
            CreateMessage::new().content(request_contents.message),
        )
        .await;

    let output = match response {
        Ok(_) => {
            info!("Message sent successfully");
            "Discord Bot Message sent successfully".to_string()
        }
        Err(err) => {
            error!("Message failed to send");
            format!["Error: {}", err]
        }
    };
    output
}

pub async fn embed(payload: String) -> String {
    info!("Received embed request: {:?}", payload);

    let request_contents: Message =
        serde_json::from_str(payload.as_str()).expect("Unable to parse message");

    let target = get_target(request_contents.channel).expect("Unable to get valid target channel");

    let channel_id = ChannelId::from(target);

    let title = if request_contents.title.is_some() {
        request_contents.title.unwrap()
    } else {
        panic!("Title is required for an embed")
    };

    let message = if request_contents.attachment.is_some() {
        let attachment = CreateAttachment::path(request_contents.attachment.unwrap())
            .await
            .expect("Unable to create attachment from path");

        CreateMessage::new()
            .embed(
                CreateEmbed::new()
                    .title(title)
                    .description(request_contents.message),
            )
            .add_file(attachment)
    } else {
        CreateMessage::new().embed(
            CreateEmbed::new()
                .title(title)
                .description(request_contents.message),
        )
    };
    let response = channel_id.send_message(&BotCache::get(), message).await;

    let output = match response {
        Ok(_) => {
            info!("Message sent successfully");
            "Discord Bot Embed sent successfully".to_string()
        }
        Err(err) => {
            error!("Message failed to send");
            format!["Error: {}", err]
        }
    };
    output
}
