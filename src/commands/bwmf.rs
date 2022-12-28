use serenity::builder::CreateApplicationCommand;
use serenity::model::prelude::interaction::application_command::CommandDataOption;

pub fn run(_options: &[CommandDataOption]) -> String {
    "https://github.com/BourbonWarfare/bwmf/archive/refs/heads/master.zip".to_string()
}

pub fn register(command: &mut CreateApplicationCommand) -> &mut CreateApplicationCommand {
    command.name("bwmf").description("Download the latest Mission Framework")
}
