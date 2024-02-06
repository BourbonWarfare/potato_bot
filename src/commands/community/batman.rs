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

    let bat_path = env::var("BAT_FILE_PATH").expect("Expected GUILD_ID in environment");

    let path = Path::new(bat_path.as_str());

    let bat_file = AttachmentType::from(path);

    embed
        .title("🦇 batman")
        .description("I Am Vengeance. I Am The Night. I Am Batman!");

    command
        .create_interaction_response(&ctx.http, |response| {
            response
                .kind(InteractionResponseType::ChannelMessageWithSource)
                .interaction_response_data(|message| {
                    message.add_file(bat_file).add_embed(embed).ephemeral(true)
                })
        })
        .await
}

pub fn register(command: &mut CreateApplicationCommand) -> &mut CreateApplicationCommand {
    command
        .name("imbatman")
        .description("For those of us who can't go on without a bat file.")
}
