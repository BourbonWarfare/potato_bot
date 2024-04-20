use crate::prelude::*;

#[derive(Serialize, Deserialize)]
struct Data {
    server: String,
    action: String,
}

pub async fn run(ctx: &Context, interaction: &CommandInteraction) -> PotatoBotResult {
    match get_option!(&interaction.data, "server", String) {
        Ok(servername) => {
            info!("Servername: {}", servername);

            match get_option!(&interaction.data, "action", String) {
                Ok(action) => {
                    info!("Action: {}", action);

                    let data = Data {
                        server: servername.to_string(),
                        action: action.to_string(),
                    };

                    let callback = |payload: Payload, _: SioClient| {
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
                    if let Err(e) = create_response_message!(
                        ctx,
                        interaction,
                        "Sending your request to the server",
                        true
                    ) {
                        let _ = PotatoBotError::Discord(e)
                            .send_error_response(ctx, interaction)
                            .await;
                    };

                    Ok(())
                }
                Err(e) => e.send_error_response(ctx, interaction).await,
            }
        }
        Err(e) => e.send_error_response(ctx, interaction).await,
    }
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
