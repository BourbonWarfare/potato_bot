use serenity::{
    all::{CommandInteraction, CommandOptionType, CreateCommand},
    builder::{CreateCommandOption, CreateEmbed, CreateInteractionResponseFollowup},
    model::application::{ResolvedOption, ResolvedValue},
    prelude::*,
};
use std::{collections::HashMap, env};
use tracing::{error, info};

use tokio::{fs::File, io::AsyncWriteExt};

use crate::backend::Interface;

pub async fn run(ctx: &Context, command: &CommandInteraction) -> Result<(), SerenityError> {
    let options = &command.data.options();
    let env_path = env::var("MISSIONS_UPLOAD_DIR").expect("MISSIONS_UPLOAD_DIR env var expected");
    let mut _full_path = String::new();
    let mut _title = String::new();
    let mut _description = String::new();

    if let Some(ResolvedOption {
        value: ResolvedValue::String(repo),
        ..
    }) = options.first()
    {
        _full_path = format!("{}/{}", env_path, repo);
        info!("Full_Path: {}", _full_path);

        if let Some(ResolvedOption {
            value: ResolvedValue::Attachment(attachment),
            ..
        }) = options.get(1)
        {
            if attachment.filename.contains(".pbo") {
                let final_path = format!("{}/{}", _full_path, &attachment.filename);
                info!("final_path: {}", final_path);
                info!("Attachment: {:?}", attachment);
                let content = attachment
                    .download()
                    .await
                    .expect("Error downloading file.");

                let mut file = File::create(final_path.clone()).await?;
                file.write_all(&content).await?;

                _title = format!(":white_check_mark: {}", &attachment.filename);

                _description = format!(
                    "File uploaded by **{}** to **{}** mission repo",
                    &command.user.name.as_str(),
                    repo
                );

                let mut interface = Interface::new(
            env::var("POTATO_BOT_TOKEN")
                        .expect("POTATO_BOT_TOKEN env var expected")
                );
                interface.upload(
                    repo.to_string(),
                    final_path.clone(),
                    HashMap::from([
                        ("author".to_string(), command.user.name.clone()),
                        ("changelog".to_string(), "Initial upload".to_string()),
                    ])
                ).await;
            } else {
                _title = format!(":octagonal_sign: {}", &attachment.filename);
                _description = "File is not a pbo".to_string();
                error!("File is not a pbo");
            }
            command
                .defer(&ctx.http)
                .await
                .expect("Unable to defer interaction");

            let embed = CreateEmbed::new().title(_title).description(_description);

            command
                .create_followup(
                    &ctx.http,
                    CreateInteractionResponseFollowup::new()
                        .add_embed(embed)
                        .ephemeral(true),
                )
                .await
                .expect("Unable to edit original interaction response");
        } else {
            "Please provide a valid attachment".to_string();
        }
    } else {
        panic!["Please provide a valid repo"]
    };
    Ok(())
}

pub fn register() -> CreateCommand {
    CreateCommand::new("upload")
        .description("Upload a mission.pbo")
        .add_option(
            CreateCommandOption::new(
                CommandOptionType::String,
                "upload",
                "Which mission collection are you uploading to?",
            )
            .add_string_choice("Main mission repo", "main")
            .add_string_choice("Off-night / alternate repo", "alternate")
            .add_string_choice("Public / Community Event repo", "event")
            .required(true),
        )
        .add_option(
            CreateCommandOption::new(
                CommandOptionType::Attachment,
                "mission_file",
                "Attach the mission file you wish to upload",
            )
            .required(true),
        )
}
