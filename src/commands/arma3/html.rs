use crate::prelude::*;

pub async fn run(ctx: &Context, interaction: &CommandInteraction) -> PotatoBotResult<String> {
    let path = Path::new(&*HTML_FILE_PATH);

    let embed = CreateEmbed::new()
        .title("Latest HTML")
        .description("Use this to import the current modlist into the A3 Launcher");

    let _ = create_defer_message!(ctx, interaction);

    let file = match CreateAttachment::path(path).await {
        Ok(o) => Ok(o),
        Err(e) => {
            let err = PotatoBotError::Discord(DiscordError::CannotFindFileAtPath(e));
            let _ = err.send_error_response(ctx, interaction).await;
            Err(err)
        }
    }?;

    match create_followup_embed_attachment!(ctx, interaction, embed, file, true) {
        Ok(_) => interaction_successful!(interaction),
        Err(e) => {
            let err = PotatoBotError::Discord(e);
            let _ = err.send_error_response(ctx, interaction).await;
            interaction_failed!(err, ctx, interaction)
        }
    }
}

pub fn register() -> CreateCommand {
    CreateCommand::new("html").description("Get the latest version of the BW Modlist HTML")
}
