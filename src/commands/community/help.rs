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
    let mut embed = CreateEmbed::default();

    embed
        .title("Potato-Bot help")
        .description("A list of commands for Potato-Bot
                     [Click here for more information](https://docs.bourbonwarfare.com/wiki/welcome-to-bw/potato-bot)")
        .field("/help", "This command", false)
        .field(
            "/docs",
            "A list of various sources of information pertaining to the BW community",
            false,
        )
        .field(
            "/bwmf",
            "A download link for the latest bwmf release",
            false,
        )
        .field(
            "/handbook",
            "Links to various handbooks for your reference",
            false,
        )
        .field(
            "/issue",
            "A submit an issue for various Potato tools",
            false,
        )
        .field("/orientation", "Request an orientation", false)
        .field(
            "/sessiontime",
            "A tool to help you convert between timezones",
            false,
        );

    command
        .create_interaction_response(&ctx.http, |response| {
            response
                .kind(InteractionResponseType::ChannelMessageWithSource)
                .interaction_response_data(|message| message.add_embed(embed).ephemeral(false))
        })
        .await
}

pub fn register(command: &mut CreateApplicationCommand) -> &mut CreateApplicationCommand {
    command.name("help").description("Get help with the bot")
}
