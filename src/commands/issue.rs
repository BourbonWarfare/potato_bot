use log::{
    error,
    info,
};

use crate::functions::github_api::create_issue;

use serenity::{
    builder::{
        CreateApplicationCommand,
        CreateComponents,
        CreateInputText,
        CreateEmbed,
    },
    model::application::interaction::InteractionResponseType,
    model::prelude::command::CommandOptionType,
    model::prelude::component::ActionRowComponent::InputText,
    model::prelude::interaction::application_command::{
        ApplicationCommandInteraction,
        CommandDataOption, 
        CommandDataOptionValue
    },
    collector::ModalInteractionCollectorBuilder,
    futures::StreamExt,
    model::application::component::InputTextStyle,
    prelude::*
};

pub async fn run(
    ctx: &Context,
    command: &ApplicationCommandInteraction,
    options: &[CommandDataOption]
) -> Result<(), SerenityError> {

    let option = options.get(0);
    let mut url: String = String::new();

    let content = if let Some(command_data_option) = option {
        if let Some(CommandDataOptionValue::String(commandname)) = &command_data_option.resolved { 

            let mut title_input = CreateInputText::default();
            title_input
                .required(true)
                .style(InputTextStyle::Short)
                .label("Issue Title")
                .custom_id("title")
                .placeholder("New Issue Title");

            let mut description_input = CreateInputText::default();
            description_input
                .required(true)
                .style(InputTextStyle::Paragraph)
                .label("Issue Description")
                .custom_id("description")
                .placeholder("Give as much detail as you can about the issue.");

            let mut components = CreateComponents::default();
            components
                .create_action_row(|row| row.add_input_text(title_input))
                .create_action_row(|row| row.add_input_text(description_input));

            match command
                .create_interaction_response(ctx, |response| {
                    response
                        .kind(InteractionResponseType::Modal)
                        .interaction_response_data(|modal| {
                            modal.set_components(components)
                                .custom_id("new_issue")
                                .title(format!("Create a new issue for {}", &commandname))
                        })
                })
                .await
            {
                Ok(()) => info!("Creating a new issue for {:#?}", &commandname),
                Err(error) => error!("{:#?}", error),
            }

            let collector = ModalInteractionCollectorBuilder::new(ctx)
                .filter(|int| int.data.custom_id == "new_issue")
                .collect_limit(1)
                .build();


            collector
                .then(|int| async move {
                    let (mut title, mut description) = (None, None);
                    let inputs: Vec<_> = int
                        .data
                        .components
                        .iter()
                        .flat_map(|a| a.components.iter())
                        .collect();

                    for input in inputs.iter()
                    {
                        match input {
                            InputText(input) if input.custom_id == "title" => title = Some(input.value.clone()),
                            InputText(input) if input.custom_id == "description" => description = Some(input.value.clone()),
                            _ => {
                                return error!("No input collected")
                            }
                        }
                    }
                    info!("title = {:#?}, description = {:#?}", title, description);
                    
                    url =  create_issue(
                        "BAD",
                        &title.unwrap().to_string(),
                        &description.unwrap().to_string())
                    .await
                    .unwrap();


                    match int.create_interaction_response(&ctx.http, |r| {
                        r.kind(InteractionResponseType::DeferredUpdateMessage)
                    })
                    .await
                    {
                        Ok(()) => info!("Finished creating issue for {:#?}", &commandname),
                        Err(error) => error!("Failed: {}", error),
                    }
                    info!("url: {:#?}", url);
                })
                .collect::<Vec<_>>()
                .await;

            match commandname.as_str() {
                "potato" => {
                    "potato".to_string()
                }
                "potbot" => {
                    "potbot".to_string()
                }
                "bwmf" => {
                    "bwmf".to_string()
                }
                _ => {
                    "fuck".to_string()
                }
            }
        } else {
            error!("Failed to resolve a handbook name");
            "Failed to resolve a handbook name".to_string()
        }
    } else {
        error!("Something went horribly wrong");
        "Something went horribly wrong".to_string()
    };

    let mut embed = CreateEmbed::default();

    embed
        .title("TEST")
        .description("Testing ... still")
        .url(content);

    if let Err(why) = command
        .create_followup_message(&ctx.http, |followup| {
            followup
                .add_embed(embed)
                .ephemeral(true)
        })
        .await
    {
        error!("Unable to create message response: {}", why);
    }
    Ok(())   
}

pub fn register(command: &mut CreateApplicationCommand) -> &mut CreateApplicationCommand {
    command
        .name("issue")
        .description("Create a github issue")
        .create_option(|option| {
            option
                .name("issue")
                .description("What system does this issue pertain to.")
                .kind(CommandOptionType::String)
                .required(true)
                .add_string_choice("Issue is with POTATO", "potato")
                .add_string_choice("Issue is with POTBOT", "potbot")
                .add_string_choice("Issue is with bwmf", "bwmf")
        })
}
