use serenity::{
    all::{CommandInteraction, CommandOptionType, ResolvedOption, ResolvedValue},
    builder::{
        CreateAttachment, CreateCommand, CreateCommandOption, CreateEmbed,
        CreateInteractionResponse, CreateInteractionResponseMessage,
    },
    prelude::*,
};
use std::{env, fs, path::PathBuf, time::SystemTime};
use tracing::info;

use crate::CONFIG;

pub async fn run(ctx: &Context, command: &CommandInteraction) -> Result<(), SerenityError> {
    let options = command.data.options();

    if let Some(ResolvedOption {
        value: ResolvedValue::String(server),
        ..
    }) = options.first()
    {
        let server_config = CONFIG
            .servers
            .iter()
            .find(|s| s.name == server.to_string())
            .unwrap();
        let arma_base_path = env::var("ARMA_BASE_DIR").expect("ARMA_BASE_DIR not found in env");
        let server_path = format!("{}/{}", arma_base_path, server_config.location.to_string());
        let rpt_path = format!(
            "{}/configs/{}/server/serverProfile/",
            server_path,
            server_config.name.to_string()
        );
        info!("rpt path: {}", rpt_path);
        let path = match std::fs::read_dir(rpt_path) {
            Ok(data) => {
                let mut most_recent_file: Option<(SystemTime, PathBuf)> = None;

                // Read the directory entries
                for entry in data {
                    let entry = entry.unwrap();
                    let path = entry.path();

                    // Check if the entry is a file with the .rpt extension
                    if path.is_file() && path.extension() == Some("rpt".as_ref()) {
                        // Get the metadata (modification time) of the file
                        let metadata = fs::metadata(&path).unwrap();
                        let modified_time = metadata.modified().unwrap();

                        // Compare with the current most recent file
                        if let Some((current_time, _)) = most_recent_file {
                            if modified_time > current_time {
                                most_recent_file = Some((modified_time, path));
                            }
                        } else {
                            most_recent_file = Some((modified_time, path));
                        }
                    }
                }
                most_recent_file.unwrap().1
            }
            Err(why) => panic!("Unable to read directory: {:?}", why),
        };
        let title = format!("🪵 RPT for server: {}", &server_config.name.as_str());
        let embed = CreateEmbed::default().title(title);

        command
            .create_response(
                &ctx.http,
                CreateInteractionResponse::Message(
                    CreateInteractionResponseMessage::new()
                        .add_file(CreateAttachment::path(path).await.unwrap())
                        .add_embed(embed)
                        .ephemeral(false),
                ),
            )
            .await
    } else {
        command
            .create_response(
                &ctx.http,
                CreateInteractionResponse::Message(
                    CreateInteractionResponseMessage::new()
                        .content("No valid server provided")
                        .ephemeral(false),
                ),
            )
            .await
    }
}

pub fn register() -> CreateCommand {
    let option = CreateCommandOption::new(CommandOptionType::String, "server", "Select the Server")
        .required(true)
        .add_string_choice("Main Server", "main")
        .add_string_choice("Training Server", "training")
        .add_string_choice("Alternate/Off Night Server", "alternate");

    CreateCommand::new("serverrpt")
        .description("Fetch the RPT for a given server")
        .add_option(option)
}
