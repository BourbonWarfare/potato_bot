use crate::{create_followup_embed_attachment, prelude::*};

pub async fn run(ctx: &Context, interaction: &CommandInteraction) -> PotatoBotResult<String> {
    let path = stdPath::new(&*BAT_FILE_PATH);

    let embed = CreateEmbed::new()
        .title("🦇 batman")
        .description("I Am Vengeance. I Am The Night. I Am Batman!");

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
    CreateCommand::new("imbatman")
        .description("For those of us who can't go on without a bat file.")
}
