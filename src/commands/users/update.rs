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
    let user =
        CreateCommandOption::new(CommandOptionType::User, "user", "User to perform action on")
            .required(true);

    let _ = &options.push(user);

    let action = CreateCommandOption::new(
        CommandOptionType::String,
        "action",
        "Select Action to perform on user",
    )
    .required(true)
    .add_string_choice("Update Field", "update")
    .add_string_choice("Get Value", "get")
    .add_string_choice("Get User", "get_user")
    .add_string_choice("Delete User", "delete");

    let _ = options.push(action);
    let final_options = options;

    CreateCommand::new("user_update")
        .description("Get/Update user information")
        .set_options(final_options)
}
