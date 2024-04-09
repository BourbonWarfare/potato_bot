use chrono::NaiveDate;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::io::Error;
use tracing::{error, info};

use serenity::{
    all::Colour,
    builder::{CreateAttachment, CreateEmbed, CreateMessage},
    model::id::ChannelId,
};

use crate::http::BotCache;

#[derive(Debug, Deserialize, Serialize)]
struct Message {
    message: String,
    channel: String,
    title: Option<String>,
    attachment: Option<String>,
}

impl Message {
    pub fn new(payload: Vec<Value>) -> Message {
        let mut message = Message {
            message: String::new(),
            channel: String::new(),
            title: Some(String::new()),
            attachment: Some(String::new()),
        };
        for value in payload {
            match serde_json::to_string(&value).unwrap().as_str() {
                "message" => {
                    if let Value::String(val) = value {
                        message.message = val;
                    }
                }
                "channel" => {
                    if let Value::String(val) = value {
                        message.channel = val;
                    }
                }
                "title" => {
                    if let Value::String(val) = value {
                        message.title = Some(val);
                    }
                }
                "attachment" => {
                    if let Value::String(val) = value {
                        message.attachment = Some(val);
                    }
                }
                _ => (),
            }
        }
        message
    }
}

#[derive(Debug, serde::Deserialize, serde::Serialize)]
struct Mod {
    ws_name: String,
    ws_id: String,
}

impl Mod {
    pub fn new(payload: Vec<Value>) -> Mod {
        let mut mod_s = Mod {
            ws_name: String::new(),
            ws_id: String::new(),
        };
        for value in payload {
            match serde_json::to_string(&value).unwrap().as_str() {
                "ws_name" => {
                    if let Value::String(val) = value {
                        mod_s.ws_name = val;
                    }
                }
                "ws_id" => {
                    if let Value::String(val) = value {
                        mod_s.ws_id = val;
                    }
                }
                _ => (),
            }
        }
        mod_s
    }
}

#[derive(Debug, serde::Deserialize, serde::Serialize)]
struct Session {
    thread_id: uuid::Uuid,
    date: NaiveDate,
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
        "mod_update" => {
            std::env::var("MOD_UPDATE_CHANNEL_ID").expect("MOD_UPDATE_CHANNEL_ID not found in env")
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

pub async fn message(payload: Vec<Value>) -> String {
    info!("Received message request: {:?}", payload);

    let request_contents: Message = Message::new(payload);

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

pub async fn embed(payload: Vec<Value>) -> String {
    info!("Received embed request: {:?}", payload);

    let request_contents: Message = Message::new(payload);

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

pub async fn scheduled_session_message(payload: Vec<Value>) -> String {
    info!("Received embed request: {:?}", payload);

    // TODO: Include the extra fun stuff here that will link to the session aar id etc
    /* let _request_contents: Session =
    serde_json::from_str(payload.as_str()).expect("Unable to parse message"); */

    let title = format!("Session Time T-1 Hour");
    let member_role_id = std::env::var("MEMBER_ROLE_ID").expect("MEMBER_ROLE_ID not found in env");
    let recruit_role_id =
        std::env::var("RECRUIT_ROLE_ID").expect("RECRUIT_ROLE_ID not found in env");
    let description = "Today's session starts in one hour.
Make sure that you have updated your mods.";
    let content = format!("<@&{}> and <@&{}>", member_role_id, recruit_role_id);

    let message = CreateMessage::new()
        .content(content)
        .embed(
        CreateEmbed::new()
            .title(title)
            .description(description)
            .image("https://cdn.discordapp.com/attachments/285837079139844096/724897893315641404/unknown.png?ex=661e3145&is=660bbc45&hm=e9a36f7f7af1f853e0d2188ebabd63575609d89fa07536f620742974b38121d5&")
            .colour(Colour::from_rgb(239, 79, 10)),
    );
    let channel_id = ChannelId::from(
        get_target("arma".to_string()).expect("Unable to get valid target channel"),
    );
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

pub async fn mod_update_message(payload: Vec<Value>) -> String {
    info!("Received embed request: {:?}", payload);

    let request_contents: Mod = Mod::new(payload);

    let msg = format!(
        "# __**PSM Mod update: {0}**__
[{0} Workshop Page](https://steamcommunity.com/sharedfiles/filedetails/?id={1})",
        request_contents.ws_name, request_contents.ws_id
    );

    let mut output_str = String::new();

    for ws_mod in vec!["mod_update", "tech"] {
        let target = get_target(ws_mod.to_string()).expect("Unable to get valid target channel");

        let channel_id = ChannelId::from(target);

        let response = channel_id
            .send_message(&BotCache::get(), CreateMessage::new().content(&msg))
            .await;

        let o = match response {
            Ok(_) => {
                info!("Message sent successfully");
                "Discord Bot Embed sent successfully".to_string()
            }
            Err(err) => {
                error!("Message failed to send");
                format!["Error: {}", err]
            }
        };
        output_str.push_str(&o)
    }
    output_str
}
