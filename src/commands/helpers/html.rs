use serenity::{
    all::{CommandInteraction, CreateAttachment},
    builder::{
        CreateCommand, CreateEmbed, CreateInteractionResponse, CreateInteractionResponseMessage,
    },
    prelude::*,
};
use std::env;
use std::path::Path;

pub async fn run(ctx: &Context, command: &CommandInteraction) -> Result<(), SerenityError> {
    let html_path = env::var("HTML_FILE_PATH").expect("HTML_FILE_PATH not found in env");

    let path = Path::new(html_path.as_str());

    let embed = CreateEmbed::new()
        .title("Latest HTML")
        .description("Use this to import the current modlist into the A3 Launcher");

    command
        .create_response(
            &ctx.http,
            CreateInteractionResponse::Message(
                CreateInteractionResponseMessage::new()
                    .add_file(CreateAttachment::path(path).await.unwrap())
                    .embed(embed)
                    .ephemeral(true),
            ),
        )
        .await
}

pub fn register() -> CreateCommand {
    CreateCommand::new("html").description("Get the latest version of the BW Modlist HTML")
}
