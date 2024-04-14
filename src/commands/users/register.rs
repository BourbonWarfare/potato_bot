use crate::prelude::*;

pub async fn run(ctx: &Context, command: &CommandInteraction) -> Result<(), SerenityError> {
    let modal = CreateQuickModal::new("About you")
        .timeout(std::time::Duration::from_secs(600))
        .short_field("SteamID")
        .short_field("Desired Username");
    let response = command.quick_modal(ctx, modal).await?.unwrap();

    let inputs = response.inputs;

    let json = json!({"discord_id": command.user.name, "steam_id": &inputs[0], "name": &inputs[1]});

    info!("json request for PSM: {}", json);

    let callback = |payload: Payload, _: rust_socketio::asynchronous::Client| {
        async move {
            callback_and_response!(payload);
        }
        .boxed()
    };

    emit_and_ack!(json, "create_user", callback);

    create_response_message!(
        ctx,
        response.interaction,
        "Registering your accound in PSM",
        true
    );

    Ok(())
}

pub fn register() -> CreateCommand {
    CreateCommand::new("register").description("Register user information")
}
