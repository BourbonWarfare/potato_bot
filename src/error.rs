use crate::prelude::*;

pub type PotatoResult<T = ()> = Result<T, PotatoError>;

#[derive(Error, Debug)]
pub enum PotatoError {
    #[error(transparent)]
    Config(#[from] ConfigError),
    #[error(transparent)]
    Discord(#[from] DiscordError),
    #[error(transparent)]
    Command(#[from] CommandError),
}
impl PotatoError {
    pub async fn send_error_response(
        &self,
        ctx: &Context,
        command: &CommandInteraction,
    ) -> PotatoResult {
        let embed = CreateEmbed::new()
            .title("Bot Error")
            .description(format!("{self}"));

        create_response_embed!(ctx, command, embed, true);

        error!("{self}");

        Ok(())
    }
}

#[derive(Error, Debug)]
pub enum DiscordError {
    #[error("Cannot build bot, why: {0}")]
    CannotBuildBot(SerenityError),
    #[error("Cannot start bot, why: {0}")]
    CannotStartBot(SerenityError),
    #[error("Cannot send response: {0}")]
    CannotSendResponse(SerenityError),
}

#[derive(Error, Debug)]
pub enum ConfigError {
    #[error("Cannot load enviroment: {0}")]
    CannotLoadEnviroment(dotenv::Error),
    #[error("Cannot parse config file: {0}")]
    CannotParseConfig(toml::de::Error),
}

#[derive(Error, Debug)]
pub enum CommandError {
    #[error("Cannot find command option")]
    CannotFindCommandOption,
    #[error("Cannot retrieve option value")]
    CannotRetrieveOptionValue,
    #[error("Option value is of wrong type")]
    OptionValueIsOfWrongType,
    #[error("Cannot retrieve attachement")]
    CannotRetrieveAttachment,
}
