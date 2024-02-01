use dotenv::dotenv;
use serenity::{all::GatewayIntents, Client};
use std::{env, sync::Arc};
use tokio::sync::OnceCell;
use tracing::{error, info, Level};

mod commands;
// pub mod events;
mod config;
mod functions;
mod handler;
mod http;
mod socket;

use crate::handler::Handler;
use crate::http::BotCache;

use lazy_static::lazy_static;

lazy_static! {
    static ref SOCKET: OnceCell<rust_socketio::asynchronous::Client> = OnceCell::new();
    static ref CONFIG: config::Config = config::get();
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Setup environment variables
    dotenv().ok();
    info!("Environment variables loaded");

    // Setup logging
    let _ = tracing_subscriber::fmt()
        .with_max_level(Level::INFO)
        .with_line_number(true)
        .init();

    info!("Logging initialized");

    // Configure the client with your Discord bot token in the environment.
    let token = env::var("DISCORD_TOKEN").expect("DISCORD_TOKEN not found in env");
    info!("Token found");

    // Build our client.
    info!("Building discord bot client");

    let mut client = Client::builder(&token, GatewayIntents::default())
        .event_handler(Handler)
        .await
        .expect("Error creating client");
    info!("Client built");

    // Init the http bot cache
    BotCache::init(Arc::clone(&client.http));
    info!("Bot cache initialized");

    // Init the socketio client
    let _ = socket::init().await;
    info!("Socketio client initialized");

    // Get serverlist from PSM
    // Check Server Config has been populated
    info!("Server list: {:?}", CONFIG.servers);
    info!("Mods list: {:?}", CONFIG.mods);

    // Start a single shard, and start listening to events.
    if let Err(why) = client.start().await {
        error!("Client error: {:?}", why);
    }
    Ok(())
}
