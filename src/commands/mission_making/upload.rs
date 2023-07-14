use log::{error, info};
use std::env;

use std::io::Write;
use std::path::Path;

use tokio::fs::File;
use tokio::io::AsyncWriteExt;

use serenity::{
    builder::{CreateApplicationCommand, CreateComponents, CreateEmbed, CreateInputText},
    model::prelude::command::CommandOptionType,
    model::prelude::interaction::application_command::{
        ApplicationCommandInteraction, CommandDataOption, CommandDataOptionValue,
    },
    prelude::*,
};

pub async fn run(
    ctx: &Context,
    command: &ApplicationCommandInteraction,
    options: &[CommandDataOption],
) -> Result<(), SerenityError> {
    let option_repo = options.get(0);
    let option_attachment = options.get(1);

    let mut path = String::new();
    let mut embed = CreateEmbed::default();

    if let Some(command_data_option) = option_repo {
        if let Some(CommandDataOptionValue::String(commandname)) = &command_data_option.resolved {
            match commandname.as_str() {
                "main" => {
                    path = env::var("MAIN_MISSIONS_REPO_PATH")
                        .expect("Unable to find MAIN_MISSIONS_REPO_PATH env")
                }
                "alt" => {
                    path = env::var("ALT_MISSIONS_REPO_PATH")
                        .expect("Unable to find ALT_MISSIONS_REPO_PATH env")
                }
                _ => {
                    error!("no repo given")
                }
            }
        } else {
            error!("Failed to resolve a repo name");
        }
    } else {
        error!("Something went horribly wrong");
    };
    if let Some(command_data_option) = option_attachment {
        if let Some(CommandDataOptionValue::Attachment(attachment)) = &command_data_option.resolved
        {
            info!("Attachment: {:?}", attachment);
            let content = attachment
                .download()
                .await
                .expect("Error downloading file.");
            let full_path = format!("{}/{}", &path, &attachment.filename);
            let mut file = File::create(full_path).await.expect("Error creating file");
            file.write_all(&content).await.expect("Error writing file");

            command
                .defer(&ctx.http)
                .await
                .expect("Unable to defer interaction");

            embed.title(&attachment.filename);

            command
                .edit_original_interaction_response(
                    &ctx.http,
                    |response| -> &mut serenity::builder::EditInteractionResponse {
                        response.set_embed(embed)
                    },
                )
                .await
                .expect("Unable to edit original interaction response");
        } else {
            error!("Failed to resolve a attachment");
        }
    } else {
        error!("Failed to get attachment option")
    }
    Ok(())
}

pub fn register(command: &mut CreateApplicationCommand) -> &mut CreateApplicationCommand {
    command
        .name("upload")
        .description("Upload a mission to the game server")
        .create_option(|option| {
            option
                .name("upload")
                .description("Which mission collection are you uploading to?")
                .kind(CommandOptionType::String)
                .required(true)
                .add_string_choice("Main mission repo", "main")
                .add_string_choice("Off-night / alternate repo", "alt")
        })
        .create_option(|option| {
            option
                .name("mission_file")
                .description("Attach the mission file you wish to upload")
                .kind(CommandOptionType::Attachment)
                .required(true)
        })
}
