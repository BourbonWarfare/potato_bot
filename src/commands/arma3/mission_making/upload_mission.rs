use crate::{check_attachment_filetype, prelude::*};

pub async fn run(ctx: &Context, interaction: &CommandInteraction) -> PotatoBotResult<String> {
    match get_option!(&interaction.data, "upload", String) {
        Ok(repo) => {
            let full_path = format!("{}/{}", *ARMA_MISSIONS_BASE_DIR, repo);
            info!("Full_Path: {}", full_path);

            match get_option!(&interaction.data, "mission_file", Attachment) {
                Ok(attachment_id) => {
                    if let Err(e) = create_defer_message!(ctx, interaction) {
                        let err = PotatoBotError::Discord(e);
                        interaction_failed!(err, ctx, interaction)
                    } else {
                        let attachment =
                            get_attachment_from_id!(&interaction.data, attachment_id).unwrap();
                        match check_attachment_filetype!(attachment, ".pbo") {
                            Ok(attachment) => {
                                let final_path = format!("{}/{}", full_path, &attachment.filename);
                                info!("final_path: {}", final_path);
                                info!("Attachment: {:?}", attachment);

                                let content = match attachment.download().await {
                                    Ok(o) => Ok(o),
                                    Err(e) => {
                                        let _ = PotatoBotError::Command(
                                            CommandError::CannotDownloadAttachment,
                                        )
                                        .send_error_response(ctx, interaction)
                                        .await;
                                        Err(e)
                                    }
                                }
                                .unwrap();

                                let path = match File::create(final_path).await {
                                    Ok(o) => Ok(o),
                                    Err(e) => {
                                        let err = PotatoBotError::PotatoError(PotatoError::System(
                                            SystemError::CannotCreateFileAtPath(e),
                                        ))
                                        .send_error_response(ctx, interaction)
                                        .await;
                                        Err(err)
                                    }
                                };
                                let _ = match path.unwrap().write_all(&content).await {
                                    Ok(_) => Ok(()),
                                    Err(_) => {
                                        let err = PotatoBotError::Command(
                                            CommandError::CannotRetrieveAttachment,
                                        )
                                        .send_error_response(ctx, interaction);
                                        Err(err)
                                    }
                                };

                                let title = format!(":white_check_mark: {}", &attachment.filename);

                                let description = format!(
                                    "File uploaded by **{}** to **{}** mission repo",
                                    &interaction.user.name.as_str(),
                                    repo
                                );

                                let embed =
                                    CreateEmbed::new().title(title).description(description);

                                match create_followup_embed!(ctx, interaction, embed, true) {
                                    Ok(_) => interaction_successful!(interaction),
                                    Err(e) => {
                                        let err = PotatoBotError::Discord(e);
                                        interaction_failed!(err, ctx, interaction)
                                    }
                                }
                            }
                            Err(e) => interaction_failed!(e, ctx, interaction),
                        }
                    }
                }
                Err(e) => interaction_failed!(e, ctx, interaction),
            }
        }
        Err(e) => interaction_failed!(e, ctx, interaction),
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
