use crate::prelude::*;

pub async fn run(ctx: &Context, interaction: &CommandInteraction) -> PotatoBotResult<String> {
    let modal = CreateQuickModal::new("About you")
        .timeout(std::time::Duration::from_secs(600))
        .short_field("SteamID")
        .short_field("Desired Username");
    let response = interaction.quick_modal(&ctx, modal).await.unwrap().unwrap();
    let _ = match create_acknowledge_response!(ctx, response.interaction) {
        Ok(_) => interaction_successful!(interaction),
        Err(e) => {
            let err = PotatoBotError::Discord(e);
            interaction_failed!(err, ctx, interaction)
        }
    };

    match user::DbUserItem::new(
        interaction.user.name.clone(),
        response.inputs[0].clone(),
        response.inputs[1].clone(),
    )
    .await
    {
        Ok(_) => {
            info!("Registered user in DB {}", interaction.user.name);
            let content = format!(
                "Successfully registered user {} in Database",
                interaction.user.name
            );
            match create_followup_message!(&ctx, response.interaction, content, true) {
                Ok(_) => interaction_successful!(interaction),
                Err(e) => {
                    let err = PotatoBotError::Discord(e);
                    interaction_failed!(err, ctx, interaction)
                }
            }
        }
        Err(e) => {
            let err = PotatoBotError::PotatoError(e);
            interaction_failed!(err, ctx, interaction)
        }
    }
}

pub fn register() -> CreateCommand {
    CreateCommand::new("register").description("Register user information")
}
