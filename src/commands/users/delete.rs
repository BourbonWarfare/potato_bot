use std::time::Duration;

use futures::FutureExt;
use rust_socketio::Payload;
use serde_json::json;
use serenity::builder::{CreateInteractionResponse, CreateInteractionResponseMessage};
use serenity::{
    all::{CommandInteraction, CommandOptionType},
    builder::{CreateCommand, CreateCommandOption},
    prelude::*,
};
use tracing::{error, info};

use crate::{callback_and_response, confirm_action, emit_and_ack, sent_to_server};

pub async fn run(ctx: &Context, command: &CommandInteraction) -> Result<(), SerenityError> {
    let m = command
        .channel_id
        .send_message(
            &ctx,
            confirm_action!("Are you sure?\n This will Delete all users information from PSM"),
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
            m.delete(&ctx).await.unwrap();
            panic!("Timed out");
        }
    };

    match interaction.data.custom_id.as_str() {
        "confirm" => {
            let callback = |payload: Payload, _: rust_socketio::asynchronous::Client| {
                async move {
                    callback_and_response!(payload);
                }
                .boxed()
            };

            emit_and_ack!(json!(command.data.options[0]), "delete_user", callback);

            sent_to_server!(&ctx, &command);
            m.delete(&ctx).await.unwrap();
            Ok(())
        }
        _ => {
            m.delete(&ctx).await.unwrap();
            error!("Cancel selection");
            Ok(())
        }
    }
}

pub fn register() -> CreateCommand {
    let user =
        CreateCommandOption::new(CommandOptionType::User, "user", "User to Detele").required(true);

    CreateCommand::new("user_delete")
        .description("Delete a given user from PSM")
        .add_option(user)
}
