use crate::prelude::*;

pub async fn run(ctx: &Context, interaction: &CommandInteraction) -> PotatoBotResult<String> {
    let content =
        "https://github.com/BourbonWarfare/bwmf/archive/refs/heads/master.zip".to_string();

    let embed = CreateEmbed::new()
        .title("📂 CLICK HERE to download")
        .description(
            "Or visit the GitHub:
            https://github.com/BourbonWarfare/bwmf",
        )
        .url(content);

    match create_response_embed!(ctx, interaction, embed, true) {
        Ok(_) => interaction_successful!(interaction),
        Err(e) => {
            let err = PotatoBotError::Discord(e);
            interaction_failed!(err, ctx, interaction)
        }
    }
}

pub fn register() -> CreateCommand {
    CreateCommand::new("bwmf").description("Download the latest Mission Framework")
}
