// WIP from server - not currently used/included
use serenity::model::gateway::{Activity, ActivityType, ActivityFlags};
use serenity::prelude::*;
use a2s::A2SClient;
use std::net::ToSocketAddrs;
use tokio::time::{sleep, Duration};

pub async fn update_arma3_player_count(ctx: Context, server_address: &str) {
    tokio::spawn(async move {
        loop {
            if let Ok(player_count) = get_arma3_player_count(server_address).await {
                let activity = Activity {
                    kind: ActivityType::Playing,
                    name: format!("Arma 3: {} players online", player_count),
                    url: None,
                    details: None,
                    state: None,
                    instance: Some(false),
                    application_id: None,
                    timestamps: None,
                    party: None,
                    assets: None,
                    secrets: None,
                    buttons: Vec::new(),
                    emoji: None,
                    created_at: 0,
                    flags: Some(ActivityFlags::empty()), // Ensure this is wrapped in Some if necessary
                };

                // Ensure ctx.set_activity is awaited correctly
                if let Err(err) = ctx.set_activity(Some(activity.into())) {
                    eprintln!("Failed to set activity: {:?}", err);
                }
            }

            sleep(Duration::from_secs(60)).await;
        }
    });
}

async fn get_arma3_player_count(addr: &str) -> Result<u32, Box<dyn std::error::Error>> {
    let client = A2SClient::new().await?;
    let socket_addr = addr.to_socket_addrs()?.next().unwrap();
    
    let info = client.info(socket_addr).await?;
    Ok(info.players.into())
}
