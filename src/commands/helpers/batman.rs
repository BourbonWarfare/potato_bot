use serenity::{
    all::{CommandInteraction, CreateAttachment},
    builder::{
        CreateCommand, CreateEmbed, CreateInteractionResponse, CreateInteractionResponseMessage,
    },
    prelude::*,
};
use std::{env, path::Path};

use tracing::info;

pub async fn run(ctx: &Context, command: &CommandInteraction) -> Result<(), SerenityError> {
    let bat_path = env::var("BAT_FILE_PATH").expect("BAT_FILE_PATH not found in env");

    let path = Path::new(bat_path.as_str());

    info!("bat file found at: {}", bat_path);

    let embed = CreateEmbed::new()
        .title("🦇 batman")
        .description("I Am Vengeance. I Am The Night. I Am Batman!");

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
    CreateCommand::new("imbatman")
        .description("For those of us who can't go on without a bat file.")
}
