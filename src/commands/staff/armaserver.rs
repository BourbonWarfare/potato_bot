use serde_json::json;
use serenity::builder::{CreateInteractionResponse, CreateInteractionResponseMessage};
use serenity::model::application::ResolvedValue;
use serenity::{
    all::{CommandInteraction, CommandOptionType, ResolvedOption},
    builder::{CreateCommand, CreateCommandOption},
    prelude::*,
};
use tracing::{error, info};

use crate::SOCKET;

pub async fn run(ctx: &Context, command: &CommandInteraction) -> Result<(), SerenityError> {
    let options = &command.data.options();

    let content = if let Some(ResolvedOption {
        value: ResolvedValue::String(servername),
        ..
    }) = options.first()
    {
        info!("Servername: {}", servername);
        if let Some(ResolvedOption {
            value: ResolvedValue::String(action),
            ..
        }) = options.get(1)
        {
            info!("Action: {}", action);
            let json = json!({ "name": servername, "action": action });

            let response = SOCKET
                .get()
                .expect("Unable to get socket")
                .emit("manage_arma_server", json)
                .await;

            let output = match response {
                Ok(_) => "Successfully sent command to PSM",
                Err(_) => "Error sending message to PSM",
            };

            format!(
                "Performing action [{}] on server [{}]\n{}",
                action.to_uppercase(),
                servername.to_uppercase(),
                output
            )
        } else {
            error!("Action not found");
            "No action given".to_string()
        }
    } else {
        error!("Server not found");
        "Wasn't able to get servername".to_string()
    };

    let _ = command
        .create_response(
            &ctx.http,
            CreateInteractionResponse::Message(
                CreateInteractionResponseMessage::new()
                    .content(content)
                    .ephemeral(true),
            ),
        )
        .await;
    Ok(())
}

pub fn register() -> CreateCommand {
    let mut options = Vec::new();
    let option = CreateCommandOption::new(CommandOptionType::String, "server", "Select the Server")
        .required(true)
        .add_string_choice("Main Server", "main")
        .add_string_choice("Training Server", "training")
        .add_string_choice("Event Server", "event")
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
