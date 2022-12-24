use log::error;

use serenity::builder::CreateApplicationCommand;
use serenity::model::prelude::command::CommandOptionType;
use serenity::model::prelude::interaction::application_command::{
    CommandDataOption, CommandDataOptionValue,
};

pub fn run(options: &[CommandDataOption]) -> String {
    let option = options.get(0);

    if let Some(command_data_option) = option {
        if let Some(CommandDataOptionValue::Number(value)) = command_data_option.resolved {
            format!("This is a test for now. {:?} ", value)
        } else {
            error!("Something went horribly wrong");
            "Something went horribly wrong".to_string()
        }
    } else {
        format!("This is a test for now. {:?} ", option)
    }
}

pub fn register(command: &mut CreateApplicationCommand) -> &mut CreateApplicationCommand {
    command
        .name("quote")
        .description("Submit or retrive a BW quote from your favourite member")
        .create_option(|option| {
            option
                .name("choice")
                .description("Make your choice")
                .kind(CommandOptionType::String)
                .required(true)
                .add_string_choice("Submit a new quote", 0)
                .add_string_choice("Retrieve a specific quote from a  member", 1)
                .add_string_choice("Get a random quote from a member", 2)
        })
        .create_option(|option| {
            option
                .name("member")
                .description("Who said it?")
                .kind(CommandOptionType::User)
                .required(true)
        })
}
