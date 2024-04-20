use crate::{give_user_new_role, prelude::*};

pub async fn run(ctx: &Context, interaction: &CommandInteraction) -> PotatoBotResult {
    match check_user_has_role!(ctx, interaction.user, *RECRUIT_ROLE_ID) {
        Ok(..) => {
            // Create the response to go to the recruit
            let embed = CreateEmbed::new()
                .title("📢  Calling an Orientor")
                .description(
                    "A member will reach out to set up an orientation.
                    Make sure that you have set up and tested your mods!

                    Details can be found in:
                    https://forums.bourbonwarfare.com/viewtopic.php?t=6877
                    
                    Please provide some idea of your availability below.",
                );

            if let Err(e) = create_response_embed!(&ctx, interaction, embed, false) {
                let _ = PotatoBotError::Discord(e)
                    .send_error_response(ctx, interaction)
                    .await;
            };

            // sends message to orientor role
            let content = MessageBuilder::new()
                .push("📣 ")
                .role(*ORIENTATION_ROLE_ID)
                .push_line_safe(" a new recruit is looking to get oriented.")
                .push("Please reach out to ")
                .user(interaction.user.id)
                .push(" to arrange something.")
                .build();

            let channel = ChannelId::new(*RECRUITMENT_CHANNEL_ID);

            if let Err(e) = channel
                .send_message(&ctx.http, CreateMessage::new().content(content))
                .await
            {
                let _ = PotatoBotError::Discord(DiscordError::CannotSendResponse(e))
                    .send_error_response(ctx, interaction)
                    .await;
            };

            match check_user_has_role!(ctx, interaction.user, *AWAITING_ORIENTATION_ROLE_ID) {
                Ok(..) => {
                    info!(
                        "{} Already has the Awaiting orientation role.",
                        interaction.user.name
                    )
                }
                Err(_) => {
                    if let Err(e) = give_user_new_role!(
                        ctx,
                        interaction.member.clone().unwrap(),
                        *AWAITING_ORIENTATION_ROLE_ID
                    ) {
                        let _ = Err::<PotatoBotError, _>(
                            PotatoBotError::Discord(DiscordError::CannotGiveUserRole(
                                interaction.clone().user.name,
                                RoleId::new(*AWAITING_ORIENTATION_ROLE_ID),
                                e,
                            ))
                            .send_error_response(ctx, interaction),
                        );
                    };
                }
            }

            Ok(())
        }
        Err(_) => {
            PotatoBotError::Discord(DiscordError::UserDoesNotHaveRole(
                interaction.user.clone().name,
                RoleId::new(*RECRUIT_ROLE_ID),
            ))
            .send_error_response(ctx, interaction)
            .await
        }
    }
}

pub fn register() -> CreateCommand {
    CreateCommand::new("orientation").description("Request an orientation")
}
