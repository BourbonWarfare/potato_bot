use crate::prelude::*;

pub async fn run(ctx: &Context, interaction: &CommandInteraction) -> PotatoBotResult {
    let m = interaction
        .channel_id
        .send_message(
            &ctx,
            confirm_action!("Are you sure?\n This will require shutting down all running servers"),
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
            let callback = |payload: Payload, _: SioClient| {
                async move {
                    callback_and_response!(payload);
                }
                .boxed()
            };

            emit_and_ack!(json!({}), "update_arma_servers", callback);

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
    CreateCommand::new("update_servers").description("Update all arma servers")
}
