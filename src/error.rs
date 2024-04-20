use crate::prelude::*;

pub type PotatoBotResult<T = ()> = Result<T, PotatoBotError>;

#[derive(Error, Debug)]
pub enum PotatoBotError {
    #[error(transparent)]
    PotatoError(PotatoError),
    #[error(transparent)]
    Discord(#[from] DiscordError),
    #[error(transparent)]
    Command(#[from] CommandError),
}
impl PotatoBotError {
    pub async fn send_error_response(
        &self,
        ctx: &Context,
        interaction: &CommandInteraction,
    ) -> PotatoBotResult {
        let embed = CreateEmbed::new()
            .title(":octagonal_sign: Potato Bot Error")
            .field(
                "",
                format!(
                    "Reach out to <@&{}> or <@{}> if error persists.",
                    *STAFF_ROLE_ID, *MAINTAINER_DISCORD_ID
                ),
                false,
            )
            .field(
                "",
                "Or open an issue, https://github.com/BourbonWarfare/potato_bot/issues",
                false,
            )
            .description(format!("```json\n{self}```"));

        match create_followup_embed!(ctx, interaction, embed, true) {
            Ok(_) => {
                info!("Response error encountered. Sent error message response to user");
                Ok(())
            }
            Err(e) => {
                error!("Response error encountered. Unable to send error messager to user");
                Err(PotatoBotError::Discord(e))
            }
        }
    }
}

#[derive(Error, Debug)]
#[error("{0}")]
pub enum DiscordError {
    #[error("Cannot build bot, why: {0}")]
    CannotBuildBot(SerenityError),
    #[error("Cannot start bot, why: {0}")]
    CannotStartBot(SerenityError),
    #[error("Cannot send response: {0}")]
    CannotSendResponse(SerenityError),
    #[error("Cannot send messages: {0}")]
    CannotSendMessage(SerenityError),
    #[error("User {0} has not got the role <@&{1}>")]
    UserDoesNotHaveRole(String, RoleId),
    #[error("User {0} has already got the role <@&{1}>")]
    UserAlreadyHasRole(String, RoleId),
    #[error("Unable to get user {0} role <@&{1}>. Error: {2}")]
    CannotGiveUserRole(String, RoleId, SerenityError),
    #[error("Unable to find file at given path: {0}")]
    CannotFindFileAtPath(SerenityError),
}

#[derive(Error, Debug)]
#[error("{0}")]
pub enum CommandError {
    #[error("Cannot find command option")]
    CannotFindCommandOption,
    #[error("Cannot register command.")]
    CannotRegisterCommand(),
    #[error("Cannot find a slash command by that name")]
    CannotFindSlashCommand(),
    #[error("Cannot retrieve option value")]
    CannotRetrieveOptionValue,
    #[error("Option value is of wrong type")]
    OptionValueIsOfWrongType,
    #[error("Cannot retrieve attachement")]
    CannotRetrieveAttachment,
    #[error("Cannot download attachement to host.")]
    CannotDownloadAttachment,
    #[error("Attachment is of wrong type: {0}")]
    InvalidAttachmentExtension(String),
    #[error("Cannot create response modal. Error: {0}")]
    UnableToCreateModal(SerenityError),
}
