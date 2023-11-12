mod commands;
mod events;
mod functions;

use log::{debug, error, info};
use log4rs;

use dotenv::dotenv;
use std::env;
use std::{mem::MaybeUninit, sync::Arc};

use serenity::async_trait;
use serenity::model::application::interaction::Interaction;
use serenity::model::gateway::Ready;
use serenity::model::id::GuildId;
use serenity::prelude::*;

use commands::community;
use commands::mission_making;
use commands::potato;
use commands::recruitment;
use commands::session;

use axum::{routing::post, Router};
use std::net::SocketAddr;

struct Handler;

pub struct CacheAndHttp();

static mut SINGLETON: MaybeUninit<Arc<serenity::CacheAndHttp>> = MaybeUninit::uninit();

impl CacheAndHttp {
    /// Gets a reference to the Bot cache and http
    ///
    /// # Panics
    ///
    /// Panics if the bot does not exists
    pub fn get() -> Arc<serenity::CacheAndHttp> {
        unsafe { SINGLETON.assume_init_ref().clone() }
    }

    /// Initializes the Bot cache and http
    pub fn init(bot: Arc<serenity::CacheAndHttp>) {
        unsafe {
            SINGLETON = MaybeUninit::new(bot);
        }
    }
}

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
                "upload" => {
                    mission_making::upload::run(&ctx, &command, &command.data.options).await
                }
                "handbook" => {
                    recruitment::handbook::run(&ctx, &command, &command.data.options).await
                }
                "issue" => potato::issue::run(&ctx, &command, &command.data.options).await,
                "orientation" => {
                    recruitment::orientation::run(&ctx, &command, &command.data.options).await
                }
                "help" => community::help::run(&ctx, &command, &command.data.options).await,
                "docs" => community::docs::run(&ctx, &command, &command.data.options).await,
                "imbatman" => community::batman::run(&ctx, &command, &command.data.options).await,
                "leadership_feedback" => session::leadership_feedback::run(&ctx, &command).await,
                _ => Err(SerenityError::Other("No slash command by that name")),
            };
            info!("Executed command interaction: {:#?}", command.data.name);
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
                .create_application_command(|command| mission_making::upload::register(command))
                .create_application_command(|command| session::sessiontime::register(command))
                .create_application_command(|command| community::batman::register(command))
                .create_application_command(|command| community::docs::register(command))
                .create_application_command(|command| community::help::register(command))
                .create_application_command(|command| {
                    session::leadership_feedback::register(command)
                })
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
    let mut client = Client::builder(token, GatewayIntents::empty())
        .event_handler(Handler)
        .await
        .expect("Error creating client");

    // Use CacheAndHttp to avoid having to clone the client before passing it
    // into the handler, and so that we can access the context and http externally.
    CacheAndHttp::init(Arc::clone(&client.cache_and_http));

    let app = Router::new()
        .route("/message", post(events::message::message))
        .route("/embed", post(events::message::embed));

    tokio::spawn(async {
        let addr = SocketAddr::from(([127, 0, 0, 1], 8082));
        println!("Server started, listening on {addr}");
        axum::Server::bind(&addr)
            .serve(app.into_make_service())
            .await
            .expect("Failed to start server");
    });

    // Finally, start a single shard, and start listening to events.
    //
    // Shards will automatically attempt to reconnect, and will perform
    // exponential backoff until it reconnects.
    if let Err(why) = client.start().await {
        error!("Client error: {:?}", why);
    }
}
