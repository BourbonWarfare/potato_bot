use crate::commands::{helpers, mission_making, recruitment, staff};

use serenity::{
    all::Interaction,
    async_trait,
    model::{gateway::Ready, id::GuildId},
    prelude::*,
};

use std::env;
use tracing::info;

pub struct Handler;

#[async_trait]
impl EventHandler for Handler {
    async fn interaction_create(&self, ctx: Context, interaction: Interaction) {
        if let Interaction::Command(command) = interaction {
            info!(
                "Received command interaction: {:#?} from: {:#?}",
                command.data.name, command.user.name
            );

            let output: Result<(), SerenityError> = match command.data.name.as_str() {
                // Helper commands
                "imbatman" => helpers::batman::run(&ctx, &command).await,
                "docs" => helpers::docs::run(&ctx, &command).await,
                "help" => helpers::help::run(&ctx, &command).await,
                "html" => helpers::html::run(&ctx, &command).await,
                "issue" => helpers::issue::run(&ctx, &command).await,
				"ping" => helpers::ping::run(&ctx, &command).await,
                "leadership_feedback" => helpers::leadership_feedback::run(&ctx, &command).await,
                "sessiontime" => helpers::sessiontime::run(&ctx, &command).await,
                // Mission making commands
                "bwmf" => mission_making::get_bwmf::run(&ctx, &command).await,
                "upload" => mission_making::upload_mission::run(&ctx, &command).await,
                // Recruitment commands
                "handbook" => recruitment::handbook::run(&ctx, &command).await,
                "orientation" => recruitment::request_orientation::run(&ctx, &command).await,
                // Staff commands
                "armaserver" => staff::armaserver::run(&ctx, &command).await,
                "aar_template" => staff::create_aar::run(&ctx, &command).await,
                "rpt" => staff::get_rpt::run(&ctx, &command).await,
                "serverstatus" => staff::serverstatus::run(&ctx, &command).await,
                "update_mods" => staff::update_mods::run(&ctx, &command).await,
                "update_servers" => staff::update_servers::run(&ctx, &command).await,
                _ => Err(SerenityError::Other("No slash command by that name")),
            };
            info!("Executed command interaction: {:#?}", command.data.name);
            info!("Returned: {:?}", output)
        }
    }

    async fn ready(&self, ctx: Context, ready: Ready) {
        info!("{} is connected!", ready.user.name);

        let guild_id = GuildId::new(
            env::var("GUILD_ID")
                .expect("GUILD_ID not found in env")
                .parse()
                .expect("GUILD_ID must be an integer"),
        );

        let commands = guild_id
            .set_commands(
                &ctx.http,
                vec![
                    // Helper commands
                    helpers::batman::register(),
                    helpers::docs::register(),
                    helpers::help::register(),
                    helpers::html::register(),
                    helpers::issue::register(),
                    helpers::leadership_feedback::register(),
					helpers::ping::register(),
                    helpers::sessiontime::register(),
                    // Mission making commands
                    mission_making::get_bwmf::register(),
                    mission_making::upload_mission::register(),
                    // Recruitment commands
                    recruitment::handbook::register(),
                    recruitment::request_orientation::register(),
                    // Staff commands
                    staff::armaserver::register(),
                    staff::create_aar::register(),
                    staff::get_rpt::register(),
                    staff::serverstatus::register(),
                    staff::update_mods::register(),
                    staff::update_servers::register(),
                ],
            )
            .await;

        info!(
            "I now have the following guild slash commands: {:#?}",
            commands
        );
    }
}
