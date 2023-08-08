mod commands;
mod functions;

use log::{debug, error, info};
use log4rs;

use dotenv::dotenv;
use std::env;

use serenity::async_trait;
use serenity::model::application::interaction::Interaction;
use serenity::model::gateway::Ready;
use serenity::model::id::GuildId;
use serenity::prelude::*;

use commands::mission_making;
use commands::potato;
use commands::recruitment;
use commands::session;

struct Handler;

#[async_trait]
impl EventHandler for Handler {
    async fn interaction_create(&self, ctx: Context, interaction: Interaction) {
        if let Interaction::ApplicationCommand(command) = interaction {
            info!(
                "Received command interaction: {:#?} from: {:#?}",
                command.data.name, command.user.name
            );

            let output: Result<(), SerenityError> = match command.data.name.as_str() {
                "sessiontime" => {
                    session::sessiontime::run(&ctx, &command, &command.data.options).await
                }
                "bwmf" => mission_making::bwmf::run(&ctx, &command, &command.data.options).await,
                "handbook" => {
                    recruitment::handbook::run(&ctx, &command, &command.data.options).await
                }
                "issue" => potato::issue::run(&ctx, &command, &command.data.options).await,
                "orientation" => {
                    recruitment::orientation::run(&ctx, &command, &command.data.options).await
                }
                "upload" => {
                    mission_making::upload::run(&ctx, &command, &command.data.options).await
                }
                _ => Err(SerenityError::Other("No slash command by that name")),
            };
            info!("Returned: {:#?}", output)
        }
    }

    async fn ready(&self, ctx: Context, ready: Ready) {
        info!("{} is connected!", ready.user.name);

        let guild_id = GuildId(
            env::var("GUILD_ID")
                .expect("Expected GUILD_ID in environment")
                .parse()
                .expect("GUILD_ID must be an integer"),
        );

        let commands = GuildId::set_application_commands(&guild_id, &ctx.http, |commands| {
            commands
                .create_application_command(|command| recruitment::handbook::register(command))
                .create_application_command(|command| recruitment::orientation::register(command))
                .create_application_command(|command| potato::issue::register(command))
                .create_application_command(|command| mission_making::bwmf::register(command))
                .create_application_command(|command| session::sessiontime::register(command))
                .create_application_command(|command| mission_making::upload::register(command))
        })
        .await;

        info!(
            "I now have the following guild slash commands: {:#?}",
            commands
        );
    }
}

#[tokio::main]
async fn main() {
    // Load env
    dotenv().ok();
    // Enable Logging
    log4rs::init_file("config/log4rs.yaml", Default::default()).unwrap();
    // Configure the client with your Discord bot token in the environment.
    let token = env::var("DISCORD_TOKEN").expect("Expected a token in the environment");

    // Build our client.
    debug!("Building client");
    let intents =
        GatewayIntents::GUILDS | GatewayIntents::GUILD_MESSAGES | GatewayIntents::MESSAGE_CONTENT;
    let mut client = Client::builder(token, intents)
        .event_handler(Handler)
        .await
        .expect("Error creating client");

    // Finally, start a single shard, and start listening to events.
    //
    // Shards will automatically attempt to reconnect, and will perform
    // exponential backoff until it reconnects.
    if let Err(why) = client.start().await {
        error!("Client error: {:?}", why);
    }
}
