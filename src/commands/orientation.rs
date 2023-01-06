use log::{
    error,
    info,
};

use serenity::{
    builder::{CreateApplicationCommand, CreateEmbed},
    model::id::ChannelId,
    model::prelude::{interaction::{
        application_command::{
            ApplicationCommandInteraction,
            CommandDataOption, 
        },
        InteractionResponseType}, RoleId},
    prelude::*, 
    utils::MessageBuilder,
};

use std::env;

pub async fn run(
    ctx: &Context,
    command: &ApplicationCommandInteraction,
    _options: &[CommandDataOption]
) -> Result<(), SerenityError> {

    let member = command.member.clone();

    let orientor_role: u64 = env::var("ORIENTATION_ROLE")
        .expect("ORIENTATION_ROLE env var expected")
        .parse()
        .expect("Expected a roleId integer");

    let awaiting_role: u64 = env::var("AWAITING_ORIENTATION_ROLE")
        .expect("AWAITING_ORIENTATION_ROLE env var expected")
        .parse()
        .expect("Expected a roleId integer");

    // Check that caller is recruit
    let recruit_role: u64 = env::var("RECRUIT_ROLE")
        .expect("RECRUIT_ROLE env var expected")
        .parse()
        .expect("Expected a roleId integer");

    if command.user.has_role(&ctx.http, command.guild_id.unwrap(), RoleId(recruit_role)).await.unwrap() {

        // Create the response to go to the recruit

        let mut embed = CreateEmbed::default();

        embed
            .title("📢 Calling an Orientor")
            .description(
                "A member will reach out to set up an orientation.
                Make sure that you have set up and tested your mods!

                Details can be found in:
                https://forums.bourbonwarfare.com/viewtopic.php?t=6877"
            );

        if let Err(error) = command
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
        {
            error!("{:#?}", error);
        };

        // sends message to orientor role

        let content = MessageBuilder::new()
            .push("📣 ").role(orientor_role)
            .push_line_safe(" a new recruit is looking to get oriented.")
            .push("Please reach out to ").user(command.user.id).push(" to arrange something.")
            .build();


        let channel = ChannelId(
            env::var("MEMBER_CHANNEL")
                .expect("expected a str containing a channel id.")
                .parse()
                .expect("Expected a ChannelId integer")
        );

        if let Err(error) = channel
            .send_message(&ctx.http, |message|{
                message
                    .content(content)
            })
        .await
        {
            error!("{:#?}", error);
        };

        match &command.user.has_role(&ctx.http, command.guild_id.unwrap(), RoleId(awaiting_role)).await.unwrap() {

            true => {
                info!("{} Already has the Awaiting orientation role.", command.user.name)
            },
            false => {
                member.unwrap().add_role(&ctx.http, awaiting_role).await;
                info!("Added the Awaiting orientation role to {}", command.user.name)
            },
        };
    } else {
        
        let mut embed = CreateEmbed::default();

        embed
            .title("⚠ You are not a recruit")
            .description("This is only intended for those with the recruit role");
        
        if let Err(error) = command
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
        {
            error!("{:#?}", error);
        };
    };

    Ok(())
}

pub fn register(command: &mut CreateApplicationCommand) -> &mut CreateApplicationCommand {
    command
        .name("orientation")
        .description("Request an orientation")
}
