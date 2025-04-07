use chrono::NaiveDate;
use std::io::Error;
use tokio::sync::Mutex;
use tracing::{error, info};

use lazy_static::lazy_static;
use serenity::{
    all::{Colour, Mention, MessageId, ReactionType, UserId},
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

#[derive(Debug, serde::Deserialize, serde::Serialize)]
struct Mod {
    ws_name: String,
    ws_id: String,
}

#[derive(Debug, serde::Deserialize, serde::Serialize)]
struct Session {
    thread_id: uuid::Uuid,
    date: NaiveDate,
}

lazy_static! {
    /// static var containing the last session reminder message id
    static ref SESSION_MESSAGE: Mutex<Option<MessageId>> = Mutex::new(None);
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

    if title.to_lowercase() == "mission end: tvt" {
        coop_ping_tvt_finished().await
    }

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

pub async fn scheduled_session_message(payload: String) -> String {
    info!("Received embed request: {:?}", payload);

    // TODO: Include the extra fun stuff here that will link to the session aar id etc
    /* let _request_contents: Session =
    serde_json::from_str(payload.as_str()).expect("Unable to parse message"); */

    let title = format!("Session Time T-1 Hour");
    let member_role_id = std::env::var("MEMBER_ROLE_ID").expect("MEMBER_ROLE_ID not found in env");
    let recruit_role_id =
        std::env::var("RECRUIT_ROLE_ID").expect("RECRUIT_ROLE_ID not found in env");
    let description = format!(
        "<@&{}> and <@&{}> session time starts in one hour.
Make sure that you have updated your mods.",
        member_role_id, recruit_role_id
    );

    let message = CreateMessage::new()
        .content(description)
        .embed(CreateEmbed::new()
            .title(title)
            .image("https://cdn.discordapp.com/attachments/285837079139844096/724897893315641404/unknown.png?ex=661e3145&is=660bbc45&hm=e9a36f7f7af1f853e0d2188ebabd63575609d89fa07536f620742974b38121d5&")
            .colour(Colour::from_rgb(239, 79, 10)),
    );
    let channel_id = ChannelId::from(
        get_target("arma".to_string()).expect("Unable to get valid target channel"),
    );
    let response = channel_id.send_message(&BotCache::get(), message).await;

    let output = match response {
        Ok(message) => {
            coop_ping_save_session_reminder(&message.id).await;
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

pub async fn mod_update_message(payload: String) -> String {
    info!("Received embed request: {:?}", payload);

    let request_contents: Mod =
        serde_json::from_str(payload.as_str()).expect("Unable to parse message");

    let msg = format!(
        "# __**Mod Updated: {0}**__
[{0}](https://steamcommunity.com/sharedfiles/filedetails/?id={1})",
        request_contents.ws_name, request_contents.ws_id
    );

    let mut output_str = String::new();

    for ws_mod in vec!["tech"] {
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

/// Saves message id from session reminder ping
async fn coop_ping_save_session_reminder(id: &MessageId) {
    info!("coop_ping_save_session_reminder: {:?}", id);
    let mut lock = SESSION_MESSAGE.lock().await;
    *lock = Some(*id);
}
/// Sends mention ping to all users who reacted with specific emoji
async fn coop_ping_tvt_finished() {
    let mut lock = SESSION_MESSAGE.lock().await;
    info!("coop_ping_tvt_finished: {:?}", *lock);
    let Some(message_id) = *lock else { return };
    *lock = None;
    let channel_id = ChannelId::from(
        get_target("arma".to_string()).expect("Unable to get valid target channel"),
    );
    let reaction_type = ReactionType::from('🍎');
    let reaction_users = channel_id
        .reaction_users(&BotCache::get(), message_id, reaction_type, None, None)
        .await;
    let Ok(reaction_users) = reaction_users else {
        return;
    };

    let mut message = String::from("CO-OP Slotting Now");
    for user in &reaction_users {
        info!(" -reacted by {}", user); // testing
        message += &format!(" {}", Mention::from(UserId::from(user)));
    }

    let response = channel_id
        .send_message(&BotCache::get(), CreateMessage::new().content(message))
        .await;
    info!("coop_ping_tvt_finished sent {:?}", response);
}
