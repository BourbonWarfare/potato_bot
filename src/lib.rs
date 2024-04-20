pub mod commands;
pub mod error;
pub mod events;
pub mod functions;
pub mod handler;
pub mod http;
pub mod macros;
pub mod meta;
pub mod prelude;
pub mod socket;

use crate::prelude::*;

pub async fn start_bot() -> Result<(), Box<dyn std::error::Error>> {
    // Setup logging
    let _ = tracing_subscriber::fmt()
        .with_max_level(Level::INFO)
        .with_line_number(true)
        .with_ansi(false)
        .with_timer(ChronoLocal::rfc_3339())
        .init();

    info!("Logging initialized");

    // Setup environment variables
    dotenv().ok();
    info!("Environment variables loaded");

    // Init Meta data
    meta::init();
    info!("Metadata initialized");

    // Configure the client with your Discord bot token in the environment.
    let token = &*DISCORD_TOKEN;
    info!("Token found");

    // Start sqlite database
    db::init().await;

    // Build our client.
    info!("Building discord bot client");

    let mut client = Client::builder(&token, GatewayIntents::default())
        .event_handler(handler::Handler)
        .await
        .expect("Error creating client");
    info!("Client built");

    // Init the http bot cache
    http::BotCache::init(Arc::clone(&client.http));
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
