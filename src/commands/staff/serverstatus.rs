use std::time::Duration;
use tracing::info;

use a2s::A2SClient;
use regex::Regex;
use serde::{Deserialize, Serialize};
use serenity::{
    all::{CommandInteraction, CommandOptionType, CreateCommand},
    builder::{
        CreateCommandOption, CreateEmbed, CreateInteractionResponse,
        CreateInteractionResponseMessage,
    },
    prelude::*,
};
use tokio::time::timeout;

use crate::SERVERLIST;

#[derive(Serialize, Deserialize, Debug)]
struct EmbedData {
    pub name: String,
    pub game: String,
    pub map: String,
    pub players: String,
    pub state: String,
}

impl<'a> EmbedData {
    fn new(data: &ServerData) -> EmbedData {
        let status_vec = vec![
            "NONE",
            "SELECTING MISSION",
            "EDITING MISSION",
            "ASSIGNING ROLES",
            "SENDING MISSION",
            "LOADING MISSION",
            "BRIEFING",
            "PLAYING",
            "DEBRIEFING",
            "MISSION ABORTED",
        ];
        let status = match &data.extended_server_info {
            Some(ext_info) => {
                let re = Regex::new(r"(?:,s)([0-9])").unwrap();
                let data_text = &ext_info.keywords.clone().unwrap();
                let caps = re.captures(data_text.as_str()).unwrap();
                let state_index: usize = caps[1].parse().unwrap();
                status_vec[state_index].to_string()
            }
            None => "OFFLINE".to_string(),
        };
        EmbedData {
            name: data.name.to_string(),
            game: data.game.to_string(),
            map: data.map.to_string(),
            players: format!(
                "{}/{}",
                data.players.to_string(),
                data.max_players.to_string()
            ),
            state: status,
        }
    }
}

#[derive(Serialize, Deserialize, Debug)]
pub struct ServerData {
    pub name: String,
    pub game: String,
    pub map: String,
    pub players: u8,
    pub max_players: u8,
    pub extended_server_info: Option<a2s::info::ExtendedServerInfo>,
}

pub async fn get_server_status(
    target_server: &String,
    target_server_pn: Option<&String>,
) -> ServerData {
    let client = A2SClient::new().await.expect("Unable to create A2S client");
    let server = SERVERLIST
        .get()
        .expect("unable to get valid server list")
        .iter()
        .find(|s| s.name == *target_server);

    let game_port: String = server.expect("").game_port.to_owned();
    let steam_port: u16 = game_port
        .parse::<u16>()
        .expect("Unable to parse an int from the game_port value")
        + 1;

    info!("127.0.0.1:{}", steam_port);

    let info = timeout(
        Duration::from_millis(500),
        client.info(format!("127.0.0.1:{}", steam_port)),
    )
    .await
    .expect("Unable to reach server. Not running?");

    match info {
        Ok(response) => ServerData {
            name: target_server_pn.unwrap().to_string(),
            game: response.game,
            map: response.map,
            players: response.players,
            max_players: response.max_players,
            extended_server_info: Some(response.extended_server_info),
        },
        Err(why) => ServerData {
            name: why.to_string(),
            game: "N/A".to_string(),
            map: "N/A".to_string(),
            players: 0,
            max_players: 0,
            extended_server_info: None,
        },
    }
}

pub async fn run(ctx: &Context, command: &CommandInteraction) -> Result<(), SerenityError> {
    let option = &command.data.options.get(0);

    command
        .defer(&ctx.http)
        .await
        .expect("Unable to defer interaction");

    // Create empty list that we will iterate over
    let mut _server_list = Vec::new();

    if option.is_some() {
        _server_list = SERVERLIST
            .get()
            .expect("unable to get valid server list")
            .iter()
            .filter(|e| e.name == option.unwrap().name)
            .collect();
    } else {
        _server_list = SERVERLIST
            .get()
            .expect("unable to get valid server list")
            .iter()
            .collect();
    }

    let mut fields: Vec<(_, _, bool)> = Vec::new();

    // Get all servers details
    for server in _server_list {
        let data = get_server_status(
            &server.name.to_string(),
            Some(&server.name_pretty.to_string()),
        )
        .await;

        let field = EmbedData::new(&data);

        fields.push((
            field.name,
            format!(
                "[{}] on [{}]\n[{}]\n[{}]",
                field.game, field.map, field.players, field.state
            ),
            true,
        ));
    }

    let embed = CreateEmbed::new().title("Server Status").fields(fields);

    command
        .create_response(
            &ctx.http,
            CreateInteractionResponse::Message(
                CreateInteractionResponseMessage::new()
                    .embed(embed)
                    .ephemeral(false),
            ),
        )
        .await
}

pub fn register() -> CreateCommand {
    let option = CreateCommandOption::new(
        CommandOptionType::SubCommandGroup,
        "server",
        "Select the Server",
    );

    for server in &*SERVERLIST.get().expect("unable to get valid server list") {
        let _ = option
            .clone()
            .add_string_choice(server.name_pretty.to_string(), server.name.to_string());
    }

    CreateCommand::new("serverstatus")
        .description("Get arma servers status")
        .add_option(option)
}
