use futures::FutureExt;
use rust_socketio::Payload;
use serde::{Deserialize, Serialize};
use serenity::all::CommandDataOptionValue;
use serenity::builder::{CreateInteractionResponse, CreateInteractionResponseMessage};
use serenity::{
    all::{CommandInteraction, CommandOptionType},
    builder::{CreateCommand, CreateCommandOption},
    prelude::*,
};
use tracing::{error, info};

use crate::{callback_and_response, create_response_message, emit_and_ack, get_option};

#[derive(Serialize, Deserialize)]
struct Data {
    server: String,
    action: String,
}

pub async fn run(ctx: &Context, command: &CommandInteraction) -> Result<(), SerenityError> {
    if let Some(servername) = get_option!(&command.data, "server", String) {
        info!("Servername: {}", servername);

        if let Some(action) = get_option!(&command.data, "action", String) {
            info!("Action: {}", action);

            let data = Data {
                server: servername.to_string(),
                action: action.to_string(),
            };

            let callback = |payload: Payload, _: rust_socketio::asynchronous::Client| {
                async move {
                    callback_and_response!(payload);
                }
                .boxed()
            };

            emit_and_ack!(
                serde_json::to_string(&data).unwrap(),
                "manage_arma_server",
                callback
            );
        } else {
            error!("Action not found");
        }
    } else {
        error!("Server not found");
    };

    create_response_message!(ctx, command, "Sending your request to the server", true);

    Ok(())
}

pub fn register() -> CreateCommand {
    let mut options = Vec::new();
    let option = CreateCommandOption::new(CommandOptionType::String, "server", "Select the Server")
        .required(true)
        .add_string_choice("Main Server", "main")
        .add_string_choice("Training Server", "training")
        .add_string_choice("Alternate/Off Night Server", "alternate")
        .add_string_choice("All Servers", "all");

    let _ = &options.push(option);

    let actions = CreateCommandOption::new(CommandOptionType::String, "action", "Select Action")
        .required(true)
        .add_string_choice("Start", "start")
        .add_string_choice("Stop", "stop")
        .add_string_choice("Restart", "restart");

    let _ = options.push(actions);
    let final_options = options;

    CreateCommand::new("armaserver")
        .description("Get arma servers status")
        .set_options(final_options)
}
