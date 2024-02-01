use reqwest::header::{ACCEPT, CONTENT_TYPE};
use serenity::model::application::ResolvedValue;
use serenity::{
    all::{CommandInteraction, CommandOptionType, ResolvedOption},
    builder::{CreateCommand, CreateCommandOption, CreateEmbed, CreateInteractionResponseFollowup},
    prelude::*,
};
use std::env;
use tracing::info;

use crate::CONFIG;

pub async fn run(ctx: &Context, command: &CommandInteraction) -> Result<(), SerenityError> {
    let options = &command.data.options();

    let servername = if let Some(ResolvedOption {
        value: ResolvedValue::String(servername),
        ..
    }) = options.first()
    {
        info!("Servername: {}", servername);
        servername
    } else {
        "Error"
    };
    let action = if let Some(ResolvedOption {
        value: ResolvedValue::String(action),
        ..
    }) = options.get(1)
    {
        info!("Action: {}", action);
        action
    } else {
        "N/A"
    };

    let title = match servername {
        "all" => {
            format!("{} All Servers", &action.to_uppercase())
        }
        _ => {
            format!("{} {}", &action.to_uppercase(), &servername.to_uppercase())
        }
    };

    command
        .defer(&ctx.http)
        .await
        .expect("Unable to defer interaction");

    let mut server_info_list = Vec::new();

    let server_list_action = match servername {
        "all" => {
            for server in &CONFIG.servers {
                server_info_list.push(server)
            }
            server_info_list
        }
        _ => {
            server_info_list.push(
                &CONFIG
                    .servers
                    .iter()
                    .find(|e| e.name == servername.to_string())
                    .unwrap(),
            );
            server_info_list
        }
    };

    let mut field_name: String = String::new();
    let mut field_status: String = String::new();
    let mut error_code: String = String::new();

    let server_url = env::var("SERVER_MANGER_URL").unwrap();

    for server in &server_list_action {
        let url = format!(
            "http://{}/arma/server/{}/{}",
            &server_url.as_str(),
            &server.name.as_str(),
            &action
        );
        let rclient = reqwest::Client::new();
        let response = rclient
            .get(url)
            .header(CONTENT_TYPE, "application/json")
            .header(ACCEPT, "application/json")
            .send()
            .await;

        field_name.push_str(format!("{}\n", server.name_pretty.as_str()).as_str());

        let status = response.unwrap().status();

        match status {
            reqwest::StatusCode::OK => field_status.push_str("✅ - Command Successfull\n"),
            _ => {
                field_status.push_str("❌ - Command Failed\n");
                error_code.push_str(format!["{}\n", status.clone()].as_str());
            }
        }
    }

    let embed = CreateEmbed::new()
        .title(title)
        .field("Name", field_name, true)
        .field("Status", field_status, true)
        .field("Return Code", error_code, true);

    command
        .create_followup(
            &ctx.http,
            CreateInteractionResponseFollowup::new().add_embed(embed),
        )
        .await
        .expect("Unable to edit original interaction response");
    Ok(())
}

pub fn register() -> CreateCommand {
    let mut options = Vec::new();
    let option = CreateCommandOption::new(CommandOptionType::String, "server", "Select the Server")
        .required(true)
        .add_string_choice("Main Server", "main")
        .add_string_choice("Training Server", "training")
        .add_string_choice("Event Server", "event")
        .add_string_choice("All Servers", "all");

    let _ = &options.push(option);

    let actions = CreateCommandOption::new(CommandOptionType::String, "action", "Select Action")
        .required(true)
        .add_string_choice("Start", "start")
        .add_string_choice("Stop", "stop")
        .add_string_choice("Restart", "restart");

    let _ = options.push(actions);
    let final_options = options;

    CreateCommand::new("armaserver")
        .description("Get arma servers status")
        .set_options(final_options)
}
