use crate::prelude::*;

pub async fn run(ctx: &Context, command: &CommandInteraction) -> PotatoResult {
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
        .map_err(DiscordError::CannotSendResponse)?;
    Ok(())
}

pub fn register() -> CreateCommand {
    CreateCommand::new("html").description("Get the latest version of the BW Modlist HTML")
}
