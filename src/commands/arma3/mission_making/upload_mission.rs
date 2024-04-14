use crate::prelude::*;

pub async fn run(ctx: &Context, command: &CommandInteraction) -> PotatoResult {
    let env_path = env::var("MISSIONS_UPLOAD_DIR").expect("MISSIONS_UPLOAD_DIR env var expected");
    let mut _full_path = String::new();
    let mut _title = String::new();
    let mut _description = String::new();

    match get_option!(&command.data, "upload", String) {
        Ok(repo) => {
            _full_path = format!("{}/{:?}", env_path, repo);
            info!("Full_Path: {}", _full_path);

            match get_option!(&command.data, "mission_file", Attachment) {
                Ok(attachment_id) => {
                    let attachment = get_attachment_from_id!(&command.data, attachment_id)?;
                    if attachment.filename.contains(".pbo") {
                        let final_path = format!("{}/{}", _full_path, &attachment.filename);
                        info!("final_path: {}", final_path);
                        info!("Attachment: {:?}", attachment);
                        let content = attachment
                            .download()
                            .await
                            .expect("Error downloading file.");

                        let mut file = File::create(final_path)
                            .await
                            .expect("Unable to create file");
                        file.write_all(&content).await;

                        _title = format!(":white_check_mark: {}", &attachment.filename);

                        _description = format!(
                            "File uploaded by **{}** to **{}** mission repo",
                            &command.user.name.as_str(),
                            repo
                        );
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

                    create_response_embed!(ctx, command, embed, false);

                    Ok(())
                }
                Err(e) => {
                    e.send_error_response(ctx, command).await;
                    Err(e)
                }
            }
        }
        Err(e) => {
            e.send_error_response(ctx, command).await;
            Err(e)
        }
    }
}

pub fn register() -> CreateCommand {
    CreateCommand::new("upload")
        .description("Create a github issue")
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
