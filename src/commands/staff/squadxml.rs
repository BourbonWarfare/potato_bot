use std::{env, error::Error, fmt::Write, path::Path, sync::Arc};

use quick_xml::se::Serializer;
use serde::{Deserialize, Serialize};
use serenity::{
    all::{CommandInteraction, CommandOptionType, CreateCommand, ResolvedOption, ResolvedValue},
    builder::{CreateCommandOption, CreateInteractionResponse, CreateInteractionResponseMessage},
    prelude::*,
};
pub struct SquadXmlLock;
impl TypeMapKey for SquadXmlLock {
    type Value = Arc<Mutex<()>>;
}

pub async fn run(ctx: &Context, command: &CommandInteraction) -> Result<(), SerenityError> {
    let ResolvedOption {
        value: ResolvedValue::String(steam_id),
        ..
    } = command.data.options()[0]
    else {
        return Ok(());
    };
    let ResolvedOption {
        value: ResolvedValue::String(game_name),
        ..
    } = command.data.options()[1]
    else {
        return Ok(());
    };

    let response;
    if steam_id.chars().all(|c| c.is_ascii_digit())
        && game_name
            .chars()
            // might be more restrictive than we need, but convers everyone so far
            .all(|c| c.is_alphanumeric() || " ()/.,_!-".contains(c))
    {
        // Lock xml mutex
        let data = ctx.data.read().await;
        let _ = data
            .get::<SquadXmlLock>()
            .expect("Expected SquadXmlLock")
            .lock()
            .await;
        let result = update_xml(steam_id, game_name, "").await;
        response = if result.is_ok() {
            result.expect("ok")
        } else {
            "Err".into()
        }
    } else {
        response = "Bad Input".into();
    }

    command
        .create_response(
            &ctx.http,
            CreateInteractionResponse::Message(
                CreateInteractionResponseMessage::new()
                    .content(response)
                    .ephemeral(false),
            ),
        )
        .await
}

pub async fn register(ctx: &Context) -> CreateCommand {
    {
        let mut data = ctx.data.write().await;
        data.insert::<SquadXmlLock>(Arc::new(Mutex::new(())));
    }

    let option_id = CreateCommandOption::new(
        CommandOptionType::String,
        "steam_id",
        "steam64-id (probably starts with 765)",
    )
    .required(true);
    let option_name =
        CreateCommandOption::new(CommandOptionType::String, "game_name", "in-game name")
            .required(true);

    CreateCommand::new("squadxml")
        .description("Updates squad.xml")
        .add_option(option_id)
        .add_option(option_name)
}

// xml clockwork:
#[derive(Debug, PartialEq, Default, Serialize, Deserialize)]
#[serde(rename = "squad")]
struct Squad {
    #[serde(rename = "@nick")]
    nick: String,
    name: String,
    email: String,
    web: String,
    picture: String,
    title: String,
    #[serde(rename = "member")]
    members: Vec<Member>,
}

#[derive(Debug, PartialEq, Default, Serialize, Deserialize)]
#[serde(default)]
struct Member {
    #[serde(rename = "@id")]
    id: String,
    #[serde(rename = "@nick")]
    nick: String,
    // email: String, // drop
    // icq: String, // lol
    remark: String,
}
async fn update_xml(id: &str, nick: &str, remark: &str) -> Result<String, Box<dyn Error>> {
    let xml_path_str =
        env::var("SQUAD_XML_FILE_PATH").expect("Expected SQUAD_XML_FILE_PATH in environment");
    let xml_path = Path::new(&xml_path_str);

    // Read-in
    let str_input = tokio::fs::read_to_string(xml_path).await?;
    let mut squad: Squad = quick_xml::de::from_str(&str_input).expect("valid xml read");

    // Modify or push-new
    let response;
    if let Some(existing) = squad.members.iter_mut().find(|m| m.id == id) {
        response = "Updating".to_string();
        existing.nick = nick.into();
        existing.nick = remark.into();
    } else {
        response = "Adding".to_string();
        squad.members.push(Member {
            id: id.into(),
            nick: nick.into(),
            remark: remark.into(),
        });
    }

    // Write-back
    let mut str_output = String::new();
    str_output.write_str(
        r###"<?xml version="1.0"?>
<!DOCTYPE squad SYSTEM "squad.dtd">
<?xml-stylesheet href="squad.xsl?" type="text/xsl"?>
"###,
    )?;
    let mut serialzer = Serializer::new(&mut str_output);
    serialzer.indent(' ', 2);
    serialzer.expand_empty_elements(true);
    squad.serialize(serialzer)?;
    tokio::fs::write(xml_path, str_output).await?;

    Ok(response)
}
