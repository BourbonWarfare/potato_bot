use crate::prelude::*;

pub async fn run(ctx: &Context, interaction: &CommandInteraction) -> PotatoBotResult {
    match get_option!(&interaction.data, "servername", String) {
        Ok(servername) => match get_option!(&interaction.data, "action", String) {
            Ok(action) => {
                info!("Action: {}", action);
                let json = json!({ "name": servername, "action": action });

                let response = SOCKET_CLIENT
                    .get()
                    .expect("Unable to get socket")
                    .emit("manage_arma_server", json)
                    .await;

                let output = match response {
                    Ok(_) => "Successfully sent command to PSM",
                    Err(_) => "Error sending message to PSM",
                };

                let content = format!(
                    "Performing action [{}] on server [{}]\n{}",
                    action.to_uppercase(),
                    servername.to_uppercase(),
                    output
                );

                if let Err(e) = create_response_message!(ctx, interaction, content, true) {
                    let _ = PotatoBotError::Discord(e)
                        .send_error_response(ctx, interaction)
                        .await;
                };

                Ok(())
            }
            Err(e) => e.send_error_response(ctx, interaction).await,
        },
        Err(e) => e.send_error_response(ctx, interaction).await,
    }
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
