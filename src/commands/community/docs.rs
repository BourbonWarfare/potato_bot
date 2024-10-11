use crate::prelude::*;

pub async fn run(ctx: &Context, interaction: &CommandInteraction) -> PotatoBotResult {
    let content = "https://docs.bourbonwarfare.com/".to_string();

    let embed = CreateEmbed::new()
        .title("📚 CLICK HERE for BW documentation")
        .description("Link to BWs documentation and resources")
        .url(content);

    match create_response_embed!(ctx, interaction, embed, true) {
        Ok(_) => interaction_successful!(interaction),
        Err(e) => {
            PotatoBotError::Discord(e)
                .send_error_response(ctx, interaction)
                .await;
        }
    };
}

pub fn register() -> CreateCommand {
    CreateCommand::new("docs").description("Get help with the bot")
}
