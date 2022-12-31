use serenity::{
    builder::{CreateApplicationCommand, CreateEmbed},
    model::prelude::interaction::{
        application_command::{
            ApplicationCommandInteraction,
            CommandDataOption, 
        },
        InteractionResponseType},
    prelude::*,
};

pub async fn run(
    ctx: &Context,
    command: &ApplicationCommandInteraction,
    _options: &[CommandDataOption]
) -> Result<(), SerenityError> {
    let content = "https://github.com/BourbonWarfare/bwmf/archive/refs/heads/master.zip".to_string();
    
    let mut embed = CreateEmbed::default();

    embed
        .title("📂 CLICK HERE to download")
        .description(
            "Or visit the GitHub:
            https://github.com/BourbonWarfare/bwmf",
        )
        .url(content);

    command
        .create_interaction_response(&ctx.http, |response| {
            response
                .kind(InteractionResponseType::ChannelMessageWithSource)
                .interaction_response_data(|message| {
                    message
                        .add_embed(embed)
                        .ephemeral(false)
                })
        })
        .await
}

pub fn register(command: &mut CreateApplicationCommand) -> &mut CreateApplicationCommand {
    command.name("bwmf").description("Download the latest Mission Framework")
}
