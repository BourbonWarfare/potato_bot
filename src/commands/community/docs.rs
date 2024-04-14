use crate::prelude::*;

pub async fn run(ctx: &Context, command: &CommandInteraction) -> Result<(), SerenityError> {
    let content = "https://docs.bourbonwarfare.com/".to_string();

    let embed = CreateEmbed::new()
        .title("📚 CLICK HERE for BW documentation")
        .description("Link to BWs documentation and resources")
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
    CreateCommand::new("docs").description("Get help with the bot")
}
