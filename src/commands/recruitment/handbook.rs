use log::error;

use serenity::{
    builder::{CreateApplicationCommand, CreateEmbed},
    model::prelude::command::CommandOptionType,
    model::prelude::interaction::{
        application_command::{
            ApplicationCommandInteraction,
            CommandDataOption, 
            CommandDataOptionValue, 
        },
        InteractionResponseType},
    prelude::*
};

pub async fn run(
    ctx: &Context,
    command: &ApplicationCommandInteraction,
    options: &[CommandDataOption]
) -> Result<(), SerenityError> {

    let option = options.get(0);

    let content = if let Some(command_data_option) = option {
        if let Some(CommandDataOptionValue::String(commandname)) = &command_data_option.resolved { 
            match commandname.as_str() {
                "recruit" => {
                    "https://forums.bourbonwarfare.com/viewtopic.php?t=6877".to_string()
                }
                "member" => {
                    "https://forums.bourbonwarfare.com/viewtopic.php?t=579".to_string()
                }
                _ => {
                    "https://forums.bourbonwarfare.com/index.php".to_string()
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
        .title("📓 CLICK HERE to open handbook")
        .description(
            "Handbooks and other useful information can be found on our website:
        https://forums.bourbonwarfare.com/index.php",
        )
        .url(content);

    command
        .create_interaction_response(&ctx.http, |response| {
            response
                .kind(InteractionResponseType::ChannelMessageWithSource)
                .interaction_response_data(|message| {
                    message
                        .add_embed(embed)
                        .ephemeral(true)
                })
        })
        .await
}

pub fn register(command: &mut CreateApplicationCommand) -> &mut CreateApplicationCommand {
    command
        .name("handbook")
        .description("Links to our handbooks.")
        .create_option(|option| {
            option
                .name("handbook")
                .description("Select which handbook.")
                .kind(CommandOptionType::String)
                .required(true)
                .add_string_choice(
                    "📘 Recruit Handbook 😕",
                    "recruit"
                )
                .add_string_choice(
                    "📗 Member Handbook 🔫",
                    "member"
                )
        })
}
