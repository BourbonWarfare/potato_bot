use futures_util::FutureExt;
use rust_socketio::Payload;
use serde_json::json;
use serenity::builder::CreateMessage;
use serenity::{
    all::{ButtonStyle, CommandInteraction},
    builder::{
        CreateButton, CreateCommand, CreateInteractionResponse, CreateInteractionResponseMessage,
    },
};
use std::time::Duration;
use tracing::{error, info};

use serenity::prelude::*;

use crate::SOCKET;

pub async fn run(ctx: &Context, command: &CommandInteraction) -> Result<(), SerenityError> {
    let m = command
        .channel_id
        .send_message(
            &ctx,
            CreateMessage::new()
                .content("Are you sure?")
                .button(
                    CreateButton::new("confirm")
                        .style(ButtonStyle::Danger)
                        .label("Do it"),
                )
                .button(
                    CreateButton::new("cancel")
                        .style(ButtonStyle::Primary)
                        .label("Cancel"),
                ),
        )
        .await
        .unwrap();

    let interaction = match m
        .await_component_interaction(&ctx.shard)
        .timeout(Duration::from_secs(60 * 3))
        .await
    {
        Some(x) => x,
        None => {
            m.reply(&ctx, "Timed out").await.unwrap();
            panic!("Timed out");
        }
    };

    match interaction.data.custom_id.as_str() {
        "confirm" => {
            let callback = |payload: Payload, _: rust_socketio::asynchronous::Client| {
                async move {
                    match payload {
                        Payload::String(_) => info!("Successfully sent command to PSM"),
                        Payload::Binary(_) => error!("Error sending message to PSM"),
                    };
                }
                .boxed()
            };

            let output = command
                .clone()
                .create_response(
                    &ctx,
                    CreateInteractionResponse::Message(
                        CreateInteractionResponseMessage::default()
                            .ephemeral(true)
                            .content("Message has been sent to server to execute command"),
                    ),
                )
                .await;
            SOCKET
                .get()
                .expect("Unable to get socket")
                .emit_with_ack(
                    "update_arma_mods",
                    json!({}),
                    Duration::from_secs(30),
                    callback,
                )
                .await
                .expect("Error sending message to PSM");
            m.delete(&ctx).await.unwrap();
            output
        }
        _ => panic!("Cancel selection"),
    }
}

pub fn register() -> CreateCommand {
    CreateCommand::new("update_mods").description("Update all mods on the server")
}
