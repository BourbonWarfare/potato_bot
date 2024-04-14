use crate::prelude::*;

pub async fn run(ctx: &Context, command: &CommandInteraction) -> PotatoResult {
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
        .map_err(DiscordError::CannotSendResponse)?;
    Ok(())
}

pub fn register() -> CreateCommand {
    CreateCommand::new("imbatman")
        .description("For those of us who can't go on without a bat file.")
}
