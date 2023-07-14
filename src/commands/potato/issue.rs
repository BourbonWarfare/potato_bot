use log::{error, info};

use crate::functions::github_api::create_issue;

use serenity::{
    builder::{CreateApplicationCommand, CreateComponents, CreateEmbed, CreateInputText},
    collector::ModalInteractionCollectorBuilder,
    futures::StreamExt,
    model::application::component::InputTextStyle,
    model::application::interaction::InteractionResponseType,
    model::prelude::command::CommandOptionType,
    model::prelude::component::ActionRowComponent::InputText,
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
    let option = options.get(0);

    if let Some(command_data_option) = option {
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
                            modal
                                .set_components(components)
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

                    for input in inputs.iter() {
                        match input {
                            InputText(input) if input.custom_id == "title" => {
                                title = Some(input.value.clone())
                            }
                            InputText(input) if input.custom_id == "description" => {
                                description = Some(input.value.clone());
                                &description.as_mut().unwrap().push_str("\n\n Reported by: ");
                                &description.as_mut().unwrap().push_str(&command.user.name);
                            }
                            _ => return error!("No input collected"),
                        }
                    }
                    info!("title = {:#?}, description = {:#?}", title, description);

                    let mut issues_url = String::new();
                    let mut project = String::new();
                    match commandname.as_str() {
                        "potato" => {
                            project = "POTATO".to_string();
                            issues_url =
                                "https://github.com/BourbonWarfare/POTATO/issues".to_string();
                        }
                        "potbot" => {
                            project = "potato_bot".to_string();
                            issues_url =
                                "https://github.com/BourbonWarfare/potato_bot/issues".to_string();
                        }
                        "bwmf" => {
                            project = "bwmf".to_string();
                            issues_url =
                                "https://github.com/BourbonWarfare/bwmf/issues".to_string();
                        }
                        _ => {
                            error!("Shouldn't get here. Something went wrong'");
                            project = "POTATO".to_string();
                            issues_url =
                                "https://github.com/BourbonWarfare/POTATO/issues".to_string();
                        }
                    };

                    let url = create_issue(
                        &project,
                        &title.unwrap().to_string(),
                        &description.unwrap().to_string(),
                    )
                    .await;

                    match int
                        .create_interaction_response(&ctx.http, |r| {
                            r.kind(InteractionResponseType::DeferredUpdateMessage)
                        })
                        .await
                    {
                        Ok(()) => info!("Finished creating issue for {:#?}", &commandname),
                        Err(error) => error!("Failed: {}", error),
                    }

                    let mut embed = CreateEmbed::default();

                    embed
                        .title(format!("New issue created in {:#?}", &commandname))
                        .description(format!(
                            "Your new issue can be viewed using the following link
                            {}
                            or but clicking the title of this message.

                            All {} issues can be viewed here:
                            {}
                            ",
                            &url.as_ref().unwrap(),
                            &commandname,
                            issues_url
                        ))
                        .url(&url.unwrap());

                    if let Err(why) = command
                        .create_followup_message(&ctx.http, |followup| {
                            followup.add_embed(embed).ephemeral(false)
                        })
                        .await
                    {
                        error!("Unable to create message response: {}", why);
                    }
                })
                .collect::<Vec<_>>()
                .await;
        } else {
            error!("Failed to resolve a handbook name");
        }
    } else {
        error!("Something went horribly wrong");
    };
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
