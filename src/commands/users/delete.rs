use crate::prelude::*;

pub async fn run(ctx: &Context, interaction: &CommandInteraction) -> PotatoBotResult {
    match get_option!(&interaction.data, "user", User) {
        Ok(user) => {
            let m = interaction
                .channel_id
                .send_message(
                    &ctx,
                    confirm_action!(
                        "Are you sure?\n This will Delete all users information from PSM"
                    ),
                )
                .await
                .unwrap();

            let confirm_interaction = match m
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

            match confirm_interaction.data.custom_id.as_str() {
                "confirm" => {
                    let callback = |payload: Payload, _: SioClient| {
                        async move {
                            callback_and_response!(payload);
                        }
                        .boxed()
                    };

                    emit_and_ack!(
                        json!({"token": confirm_interaction.token, "discord_id": user.to_user(http::BotCache::get()).await.unwrap().name}),
                        "delete_user",
                        callback
                    );

                    sent_to_server!(&ctx, &confirm_interaction);
                    m.delete(&ctx).await.unwrap();
                    Ok(())
                }
                _ => {
                    m.delete(&ctx).await.unwrap();
                    error!("Selection Cancelled");
                    Ok(())
                }
            }
        }

        Err(e) => e.send_error_response(ctx, interaction).await,
    }
}

pub fn register() -> CreateCommand {
    let user =
        CreateCommandOption::new(CommandOptionType::User, "user", "User to Detele").required(true);

    CreateCommand::new("user_delete")
        .description("Delete a given user from PSM")
        .add_option(user)
}
