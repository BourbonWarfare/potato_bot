use serenity::{
    all::{ActionRowComponent::InputText, CommandInteraction, InputTextStyle},
    builder::{
        CreateActionRow, CreateCommand, CreateEmbed, CreateInputText, CreateInteractionResponse,
        CreateInteractionResponseFollowup, CreateInteractionResponseMessage, CreateModal,
    },
    collector::ModalInteractionCollector,
    futures::StreamExt,
};
use tracing::{error, info};

use std::fs::File;
use std::{error::Error, io::Read};

use serenity::prelude::*;

fn read_file_to_string(file_path: &str) -> Result<String, Box<dyn Error>> {
    // Open the file
    let mut file = File::open(file_path)?;

    // Read the file's contents into a string
    let mut contents = String::new();
    file.read_to_string(&mut contents)?;

    Ok(contents)
}

pub async fn run(ctx: &Context, command: &CommandInteraction) -> Result<(), SerenityError> {
    let tvt1_title = CreateInputText::new(InputTextStyle::Paragraph, "TVT1 Title", "tvt1_title")
        .required(true)
        .placeholder("Title for upcoming TVT1");
    let tvt1_description = CreateInputText::new(
        InputTextStyle::Paragraph,
        "TVT1 Description",
        "tvt1_description",
    )
    .required(true)
    .placeholder("Description of upcoming TVT1");
    let coop_title = CreateInputText::new(InputTextStyle::Paragraph, "COOP Title", "coop_title")
        .required(true)
        .placeholder("Title of upcoming COOP");
    let coop_description = CreateInputText::new(
        InputTextStyle::Paragraph,
        "COOP Description",
        "coop_description",
    )
    .required(true)
    .placeholder("Description of upcoming COOP");

    let modal = CreateModal::new("new_aar", "Create new AAR").components(vec![
        CreateActionRow::InputText(tvt1_title),
        CreateActionRow::InputText(tvt1_description),
        CreateActionRow::InputText(coop_title),
        CreateActionRow::InputText(coop_description),
    ]);

    match command
        .create_response(
            &ctx.http,
            serenity::builder::CreateInteractionResponse::Modal(modal),
        )
        .await
    {
        Ok(()) => info!("Creating new aar"),
        Err(error) => error!("{:#?}", error),
    }

    let collector = ModalInteractionCollector::new(ctx)
        .filter(|int| int.data.custom_id == "new_aar")
        .timeout(std::time::Duration::from_secs(600))
        .stream();

    collector
        .then(|input| async move {
            let (mut tvt1_title, mut tvt1_description, mut coop_title, mut coop_description) =
                (None, None, None, None);
            let inputs: Vec<_> = input
                .data
                .components
                .iter()
                .flat_map(|a| a.components.iter())
                .collect();

            for input in inputs.iter() {
                match input {
                    InputText(input) if input.custom_id == "tvt1_title" => {
                        tvt1_title = Some(input.value.clone())
                    }
                    InputText(input) if input.custom_id == "tvt1_description" => {
                        tvt1_description = Some(input.value.clone());
                    }
                    InputText(input) if input.custom_id == "coop_title" => {
                        coop_title = Some(input.value.clone());
                    }
                    InputText(input) if input.custom_id == "coop_description" => {
                        coop_description = Some(input.value.clone());
                    }
                    _ => return error!("No input collected"),
                }
            }

            match input
                .create_response(
                    &ctx.http,
                    CreateInteractionResponse::Defer(CreateInteractionResponseMessage::new()),
                )
                .await
            {
                Ok(()) => info!("Finished creating feedback template"),
                Err(error) => error!("Failed: {}", error),
            }

            let file_path = "./templates/new_aar";

            let description = match read_file_to_string(file_path) {
                Ok(contents) => {
                    info!("File contents:\n{}", contents);
                    contents
                        .replace(
                            "[tvt1_title]",
                            tvt1_title
                                .unwrap()
                                .expect("No tvt1_itle string found")
                                .as_str(),
                        )
                        .replace(
                            "[tvt1_description]",
                            tvt1_description
                                .unwrap()
                                .expect("No tvt1_description string found")
                                .as_str(),
                        )
                        .replace(
                            "[coop_title]",
                            coop_title
                                .unwrap()
                                .expect("No coop_title string found")
                                .as_str(),
                        )
                        .replace(
                            "[coop_description]",
                            coop_description
                                .unwrap()
                                .expect("No coop_description string found")
                                .as_str(),
                        )
                }
                Err(err) => {
                    error!("Error reading file: {}", err);
                    String::new()
                }
            };

            let embed = CreateEmbed::new()
                .title(format!("AAR Template created for {}", &command.user.name))
                .description(description);

            if let Err(why) = command
                .create_followup(
                    &ctx.http,
                    CreateInteractionResponseFollowup::new()
                        .add_embed(embed)
                        .ephemeral(true),
                )
                .await
            {
                error!("Unable to create message response: {}", why);
            }
        })
        .collect::<Vec<_>>()
        .await;
    Ok(())
}

pub fn register() -> CreateCommand {
    CreateCommand::new("aar_template").description("New aar template")
}
