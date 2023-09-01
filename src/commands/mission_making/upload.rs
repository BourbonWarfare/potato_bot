use log::{error, info};

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

<<<<<<< Updated upstream
    if let Some(command_data_option) = option_repo {
        if let Some(CommandDataOptionValue::String(commandname)) = &command_data_option.resolved {
            match commandname.as_str() {
                "main" => {}
                "alt" => {}
                _ => {
                    error!("no repo given")
                }
            }
=======
    let env_path = env::var("MISSIONS_UPLOAD_PATH").expect("MISSIONS_UPLOAD_PATH env var expected");
    let mut embed = CreateEmbed::default();

    if let Some(command_data_option) = option_repo {
        if let Some(CommandDataOptionValue::String(commandname)) = &command_data_option.resolved {
            info!("Repo: {:?}", commandname);
>>>>>>> Stashed changes
        } else {
            error!("Failed to resolve a repo name");
        }
    } else {
        error!("Something went horribly wrong");
    };
    if let Some(command_data_option) = option_attachment {
        if let Some(CommandDataOptionValue::Attachment(attachment)) = &command_data_option.resolved
        {
<<<<<<< Updated upstream
            info!("Attachment: {:?}", attachment);
            attachment.download().await?;
=======
            if attachment.filename.contains(".pbo") {
                let full_path = format!("{}/{}", env_path, &attachment.filename);
                info!("Attachment: {:?}", attachment);
                let content = attachment
                    .download()
                    .await
                    .expect("Error downloading file.");

                let mut file = File::create(full_path).await.expect("Error creating file");
                file.write_all(&content).await.expect("Error writing file");

                let description = format!("File uploaded by {:?}", &command.user.name);

                embed.title(&attachment.filename).description(description);
            } else {
                embed
                    .title(&attachment.filename)
                    .description("File is not a pbo");
                error!("File is not a pbo");
            }
            command
                .defer(&ctx.http)
                .await
                .expect("Unable to defer interaction");

            command
                .edit_original_interaction_response(
                    &ctx.http,
                    |response| -> &mut serenity::builder::EditInteractionResponse {
                        response.set_embed(embed)
                    },
                )
                .await
                .expect("Unable to edit original interaction response");
>>>>>>> Stashed changes
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
        .description("Create a github issue")
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
