use std::env;
use std::path::Path;

use serenity::{
    builder::{CreateApplicationCommand, CreateEmbed},
    model::prelude::{
        interaction::{
            application_command::{ApplicationCommandInteraction, CommandDataOption},
            InteractionResponseType,
        },
        AttachmentType,
    },
    prelude::*,
};
use tokio::fs::File;

pub async fn run(
    ctx: &Context,
    command: &ApplicationCommandInteraction,
    _options: &[CommandDataOption],
) -> Result<(), SerenityError> {
    let mut embed = CreateEmbed::default();

    let html_path = env::var("HTML_FILE_PATH").expect("Expected HTML_FILE_PATH in environment");

    let path = Path::new(html_path.as_str());

    let html_file = AttachmentType::from(path);

    embed
        .title("Latest HTML")
        .description("Use this to import the current modlist into the A3 Launcher");

    command
        .create_interaction_response(&ctx.http, |response| {
            response
                .kind(InteractionResponseType::ChannelMessageWithSource)
                .interaction_response_data(|message| {
                    message
                        .add_file(html_file)
                        .add_embed(embed)
                        .ephemeral(false)
                })
        })
        .await
}

pub fn register(command: &mut CreateApplicationCommand) -> &mut CreateApplicationCommand {
    command
        .name("html")
        .description("Get the latest version of the BW Modlist HTML")
}
