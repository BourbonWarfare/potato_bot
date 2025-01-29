use serenity::{
    all::CommandInteraction,
    builder::{
        CreateCommand, CreateEmbed, CreateInteractionResponse, CreateInteractionResponseMessage,
    },
    prelude::*,
};

pub async fn run(ctx: &Context, command: &CommandInteraction) -> Result<(), SerenityError> {
    let embed = CreateEmbed::new()
        .title("Pong!")
        .description("the bot works");
    command
        .create_response(
            &ctx.http,
            CreateInteractionResponse::Message(
                CreateInteractionResponseMessage::new()
                    .embed(embed)
                    .ephemeral(false),
            ),
        )
        .await
}

pub fn register() -> CreateCommand {
    CreateCommand::new("ping").description("Ping")
}
