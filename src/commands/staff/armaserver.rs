use futures_util::FutureExt;
use rust_socketio::Payload;
use serde_json::json;
use serenity::{
    all::{CommandInteraction, CommandOptionType},
    builder::{CreateCommand, CreateCommandOption, CreateEmbed, CreateInteractionResponseFollowup},
    prelude::*,
};
use tokio::time::Duration;
use tracing::{error, info};

use crate::{SERVERLIST, SOCKET};

#[derive(Debug, serde::Deserialize)]
struct Response {
    status: String,
}

pub async fn run(ctx: &Context, command: &CommandInteraction) -> Result<(), SerenityError> {
    let options = command.data.options();
    let servername = &options.get(0).unwrap().name;
    let action = &options.get(1).unwrap().name;

    info!("Server: {}", servername);

    let title = match *servername {
        "all" => {
            format!("{} All Servers", &action.to_uppercase())
        }
        _ => {
            format!("{} {}", &action.to_uppercase(), &action.to_uppercase())
        }
    };

    command
        .defer(&ctx.http)
        .await
        .expect("Unable to defer interaction");

    let mut server_info_list = Vec::new();

    let server_list_action = match *servername {
        "all" => {
            for server in &*SERVERLIST.get().expect("unable to get valid server list") {
                server_info_list.push(server)
            }
            server_info_list
        }
        _ => {
            server_info_list.push(
                SERVERLIST
                    .get()
                    .expect("unable to get valid server list")
                    .iter()
                    .find(|e| e.name == servername.to_string())
                    .unwrap(),
            );
            server_info_list
        }
    };

    let mut field_name: String = String::new();
    let mut field_status: String = String::new();

    for server in &server_list_action {
        field_name.push_str(format!("{}\n", server.name_pretty.as_str()).as_str());

        let payload = json!({
            "server": server.name,
            "action": action,
        });

        let response = SOCKET
            .get()
            .expect("unable to get valid socket")
            .emit("manage_arma_server", payload)
            .await
            .unwrap();

        match response.status.as_str() {
            "success" => field_status.push_str("✅ - Command Successfull\n"),
            _ => {
                error!("Command Failed");
                field_status.push_str("❌ - Command Failed\n")
            }
        }
    }
    let embed = CreateEmbed::new()
        .title(title)
        .field("Name", field_name, true)
        .field("Status", field_status, true);

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
        .required(true);

    for server in &*SERVERLIST.get().expect("unable to get valid server list") {
        let _ = option
            .clone()
            .add_string_choice(server.name_pretty.to_string(), server.name.to_string());
    }

    options.push(option);

    let actions = CreateCommandOption::new(CommandOptionType::String, "action", "Select Action")
        .required(true)
        .add_string_choice("Start", "start")
        .add_string_choice("Stop", "stop")
        .add_string_choice("Restart", "restart");

    options.push(actions);

    CreateCommand::new("armaserver")
        .description("Get arma servers status")
        .set_options(options)
}
