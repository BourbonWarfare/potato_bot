use crate::prelude::*;

pub async fn run(ctx: &Context, command: &CommandInteraction) -> PotatoResult {
    let content =
        "https://github.com/BourbonWarfare/bwmf/archive/refs/heads/master.zip".to_string();

    let embed = CreateEmbed::new()
        .title("📂 CLICK HERE to download")
        .description(
            "Or visit the GitHub:
            https://github.com/BourbonWarfare/bwmf",
        )
        .url(content);

    create_response_embed!(ctx, command, embed, true);

    Ok(())
}

pub fn register() -> CreateCommand {
    CreateCommand::new("bwmf").description("Download the latest Mission Framework")
}
