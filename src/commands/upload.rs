use serenity::builder::CreateApplicationCommand;
use serenity::model::prelude::command::CommandOptionType;
use serenity::model::prelude::interaction::application_command::CommandDataOption;

pub fn run(_options: &[CommandDataOption]) -> String {
    "Hey, I'm alive!".to_string()
}

pub fn register(command: &mut CreateApplicationCommand) -> &mut CreateApplicationCommand {
    command
        .name("upload")
        .description("Upload a mission and unit test")
        .create_option(|option| {
            option
                .name("server")
                .description("Server to upload mission to.")
                .kind(CommandOptionType::String)
                .required(true)
                .add_string_choice(
                    "Main Server Repo",
                    0
                )
                .add_string_choice(
                    "Offnight Server Repo",
                    1
                )
        })
        .create_option(|option| {
            option
                .name("mission")
                .description("Mission File")
                .kind(CommandOptionType::Attachment)
                .required(true)
        })
}
