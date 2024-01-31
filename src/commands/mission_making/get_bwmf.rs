use serenity::{
    all::CommandInteraction,
    builder::{
        CreateCommand, CreateEmbed, CreateInteractionResponse, CreateInteractionResponseMessage,
    },
    prelude::*,
};

pub async fn run(ctx: &Context, command: &CommandInteraction) -> Result<(), SerenityError> {
    let content =
        "https://github.com/BourbonWarfare/bwmf/archive/refs/heads/master.zip".to_string();

    let embed = CreateEmbed::new()
        .title("📂 CLICK HERE to download")
        .description(
            "Or visit the GitHub:
            https://github.com/BourbonWarfare/bwmf",
        )
        .url(content);

    command
        .create_response(
            &ctx.http,
            CreateInteractionResponse::Message(
                CreateInteractionResponseMessage::new()
                    .embed(embed)
                    .ephemeral(true),
            ),
        )
        .await
}

pub fn register() -> CreateCommand {
    CreateCommand::new("bwmf").description("Download the latest Mission Framework")
}
