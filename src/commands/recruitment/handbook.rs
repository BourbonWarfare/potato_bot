use crate::prelude::*;

pub async fn run(ctx: &Context, interaction: &CommandInteraction) -> PotatoBotResult<String> {
    match get_option!(&interaction.data, "handbook", String) {
        Ok(handbook) => {
            info!("Getting link for handbook: {}", handbook);
            let url = match handbook.as_str() {
                "recruit" => "https://docs.bourbonwarfare.com/wiki/welcome-to-bw/recruit-handbook",
                "member" => "https://forums.bourbonwarfare.com/viewtopic.php?t=579",
                _ => {
                    error!("No handbook selected");
                    "https://docs.bourbonwarfare.com/wiki/"
                }
            };
            let embed = CreateEmbed::new()
                .title("📓 CLICK HERE to open handbook")
                .description(
                "Handbooks and other useful information can be found on our website:\nhttps://docs.bourbonwarfare.com/wiki/",
                )
                .url(url);

            match create_response_embed!(&ctx, interaction, embed, true) {
                Ok(_) => interaction_successful!(interaction),
                Err(e) => {
                    let err = PotatoBotError::Discord(e);
                    interaction_failed!(err, ctx, interaction)
                }
            }
        }
        Err(e) => interaction_failed!(e, ctx, interaction),
    }
}

pub fn register() -> CreateCommand {
    CreateCommand::new("handbook")
        .description("Links to our handbooks.")
        .add_option(
            CreateCommandOption::new(
                CommandOptionType::String,
                "handbook",
                "Select which handbook",
            )
            .required(true)
            .add_string_choice("📘 Recruit Handbook 😕", "recruit")
            .add_string_choice("📗 Member Handbook 🔫", "member"),
        )
}
