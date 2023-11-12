use serenity::{
    builder::{CreateApplicationCommand, CreateEmbed},
    model::prelude::interaction::{
        application_command::{ApplicationCommandInteraction, CommandDataOption},
        InteractionResponseType,
    },
    prelude::*,
};

pub async fn run(
    ctx: &Context,
    command: &ApplicationCommandInteraction,
    _options: &[CommandDataOption],
) -> Result<(), SerenityError> {
    let content = "https://docs.bourbonwarfare.com/".to_string();

    let mut embed = CreateEmbed::default();

    embed
        .title("📚 CLICK HERE for BW documentation")
        .description("Link to BWs documentation and resources")
        .url(content);

    command
        .create_interaction_response(&ctx.http, |response| {
            response
                .kind(InteractionResponseType::ChannelMessageWithSource)
                .interaction_response_data(|message| message.add_embed(embed).ephemeral(false))
        })
        .await
}

pub fn register(command: &mut CreateApplicationCommand) -> &mut CreateApplicationCommand {
    command.name("docs").description("Get help with the bot")
}
