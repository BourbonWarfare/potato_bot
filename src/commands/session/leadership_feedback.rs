use log::{error, info};

use std::fs::File;
use std::{error::Error, io::Read};

use serenity::{
    builder::{CreateApplicationCommand, CreateComponents, CreateEmbed, CreateInputText},
    collector::ModalInteractionCollectorBuilder,
    futures::StreamExt,
    model::application::component::InputTextStyle,
    model::application::interaction::InteractionResponseType,
    model::prelude::component::ActionRowComponent::InputText,
    model::prelude::interaction::application_command::ApplicationCommandInteraction,
    prelude::*,
};

fn read_file_to_string(file_path: &str) -> Result<String, Box<dyn Error>> {
    // Open the file
    let mut file = File::open(file_path)?;

    // Read the file's contents into a string
    let mut contents = String::new();
    file.read_to_string(&mut contents)?;

    Ok(contents)
}

pub async fn run(
    ctx: &Context,
    command: &ApplicationCommandInteraction,
) -> Result<(), SerenityError> {
    let mut sustain_input = CreateInputText::default();
    sustain_input
        .required(true)
        .style(InputTextStyle::Paragraph)
        .label("Sustains")
        .custom_id("sustains")
        .placeholder("What did they do well and should keep doing going forward?");
    let mut improve_input = CreateInputText::default();
    improve_input
        .required(true)
        .style(InputTextStyle::Paragraph)
        .label("Improves")
        .custom_id("improves")
        .placeholder("What could they do better next time?");
    let mut overall_input = CreateInputText::default();
    overall_input
        .required(true)
        .style(InputTextStyle::Paragraph)
        .label("Overall")
        .custom_id("overall")
        .placeholder("Overall how do you summarize their performance?");

    let mut components = CreateComponents::default();
    components
        .create_action_row(|row| row.add_input_text(sustain_input))
        .create_action_row(|row| row.add_input_text(improve_input))
        .create_action_row(|row| row.add_input_text(overall_input));

    match command
        .create_interaction_response(ctx, |response| {
            response
                .kind(InteractionResponseType::Modal)
                .interaction_response_data(|modal| {
                    modal
                        .set_components(components)
                        .custom_id("new_feedback")
                        .title("Give feedback to member")
                })
        })
        .await
    {
        Ok(()) => info!("Creating new feedback"),
        Err(error) => error!("{:#?}", error),
    }

    let collector = ModalInteractionCollectorBuilder::new(ctx)
        .filter(|int| int.data.custom_id == "new_feedback")
        .collect_limit(1)
        .build();

    collector
        .then(|int| async move {
            let (mut sustain, mut improve, mut overall) = (None, None, None);
            let inputs: Vec<_> = int
                .data
                .components
                .iter()
                .flat_map(|a| a.components.iter())
                .collect();

            for input in inputs.iter() {
                match input {
                    InputText(input) if input.custom_id == "sustains" => {
                        sustain = Some(input.value.clone())
                    }
                    InputText(input) if input.custom_id == "improves" => {
                        improve = Some(input.value.clone());
                    }
                    InputText(input) if input.custom_id == "overall" => {
                        overall = Some(input.value.clone());
                    }
                    _ => return error!("No input collected"),
                }
            }

            match int
                .create_interaction_response(&ctx.http, |r| {
                    r.kind(InteractionResponseType::DeferredUpdateMessage)
                })
                .await
            {
                Ok(()) => info!("Finished creating feedback template"),
                Err(error) => error!("Failed: {}", error),
            }

            let mut embed = CreateEmbed::default();

            let file_path = "./templates/leadership_feedback";

            let description = match read_file_to_string(file_path) {
                Ok(contents) => {
                    info!("File contents:\n{}", contents);
                    contents
                        .replace("[sustains]", sustain.unwrap_or_default().as_str())
                        .replace("[improves]", improve.unwrap_or_default().as_str())
                        .replace("[overall]", overall.unwrap_or_default().as_str())
                }
                Err(err) => {
                    error!("Error reading file: {}", err);
                    String::new()
                }
            };

            embed
                .title(format!("Feedback Template for {}", &command.user.name))
                .description(description);

            if let Err(why) = command
                .create_followup_message(&ctx.http, |followup| {
                    followup.add_embed(embed).ephemeral(true)
                })
                .await
            {
                error!("Unable to create message response: {}", why);
            }
        })
        .collect::<Vec<_>>()
        .await;
    Ok(())
}

pub fn register(command: &mut CreateApplicationCommand) -> &mut CreateApplicationCommand {
    command
        .name("leadership_feedback")
        .description("Provide leadership feedback to a member")
}
