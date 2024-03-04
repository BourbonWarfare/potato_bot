use tracing::{error, info};

use serenity::{
    all::{ChannelId, CommandInteraction, RoleId},
    builder::{
        CreateCommand, CreateEmbed, CreateInteractionResponse, CreateInteractionResponseMessage,
        CreateMessage,
    },
    prelude::*,
    utils::MessageBuilder,
};

use std::env;

pub async fn run(ctx: &Context, command: &CommandInteraction) -> Result<(), SerenityError> {
    let member = command.member.clone();

    let orientor_role: u64 = env::var("ORIENTATION_ROLE_ID")
        .expect("ORIENTATION_ROLE_ID not found in env")
        .parse()
        .expect("Expected a roleId integer");

    let awaiting_role: u64 = env::var("AWAITING_ORIENTATION_ROLE_ID")
        .expect("AWAITING_ORIENTATION_ROLE_ID not found in env")
        .parse()
        .expect("Expected a roleId integer");

    // Check that caller is recruit
    let recruit_role: u64 = env::var("RECRUIT_ROLE_ID")
        .expect("RECRUIT_ROLE_ID not found in env")
        .parse()
        .expect("Expected a roleId integer");

    if command
        .user
        .has_role(
            &ctx.http,
            command.guild_id.unwrap(),
            RoleId::new(recruit_role),
        )
        .await
        .unwrap()
    {
        // Create the response to go to the recruit

        let embed = CreateEmbed::new()
            .title("📢 Calling an Orientor")
            .description(
                "A member will reach out to set up an orientation.
                Make sure that you have set up and tested your mods!

                Details can be found in:
                https://forums.bourbonwarfare.com/viewtopic.php?t=6877
                
                Please provide some idea of your availability below.",
            );

        if let Err(error) = command
            .create_response(
                &ctx.http,
                CreateInteractionResponse::Message(
                    CreateInteractionResponseMessage::new()
                        .add_embed(embed)
                        .ephemeral(false),
                ),
            )
            .await
        {
            error!("{:#?}", error);
        };

        // sends message to orientor role

        let content = MessageBuilder::new()
            .push("📣 ")
            .role(orientor_role)
            .push_line_safe(" a new recruit is looking to get oriented.")
            .push("Please reach out to ")
            .user(command.user.id)
            .push(" to arrange something.")
            .build();

        let channel = ChannelId::new(
            env::var("RECRUITMENT_CHANNEL_ID")
                .expect("RECRUITMENT_CHANNEL_ID not found in env")
                .parse()
                .expect("Expected a ChannelId integer"),
        );

        if let Err(error) = channel
            .send_message(&ctx.http, CreateMessage::new().content(content))
            .await
        {
            error!("{:#?}", error);
        };

        match &command
            .user
            .has_role(
                &ctx.http,
                command.guild_id.unwrap(),
                RoleId::new(awaiting_role),
            )
            .await
            .unwrap()
        {
            true => {
                info!(
                    "{} Already has the Awaiting orientation role.",
                    command.user.name
                )
            }
            false => {
                let _ = member.unwrap().add_role(&ctx.http, awaiting_role).await;
                info!(
                    "Added the Awaiting orientation role to {}",
                    command.user.name
                )
            }
        };
    } else {
        let embed = CreateEmbed::new()
            .title("⚠ You are not a recruit")
            .description("This is only intended for those with the recruit role");

        if let Err(error) = command
            .create_response(
                &ctx.http,
                CreateInteractionResponse::Message(
                    CreateInteractionResponseMessage::new()
                        .add_embed(embed)
                        .ephemeral(true),
                ),
            )
            .await
        {
            error!("{:#?}", error);
        };
    };

    Ok(())
}

pub fn register() -> CreateCommand {
    CreateCommand::new("orientation").description("Request an orientation")
}
