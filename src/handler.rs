use crate::prelude::*;

pub struct Handler;

#[async_trait]
impl EventHandler for Handler {
    async fn interaction_create(&self, ctx: Context, interaction: Interaction) {
        if let Interaction::Command(interaction) = interaction {
            info!(
                "Received command interaction: {:#?} from: {:#?}",
                interaction.data.name, interaction.user.name
            );

            let output: PotatoBotResult<String> = match interaction.data.name.as_str() {
                // Helper commands
                "docs" => community::docs::run(&ctx, &interaction).await,
                // "help" => community::help::run(&ctx, &interaction).await,
                // "issue" => community::issue::run(&ctx, &interaction).await,
                // "sessiontime" => community::sessiontime::run(&ctx, &interaction).await,
                // // Arma 3 Commands
                "html" => arma3::html::run(&ctx, &interaction).await,
                "imbatman" => arma3::batman::run(&ctx, &interaction).await,
                "leadership_feedback" => arma3::leadership_feedback::run(&ctx, &interaction).await,
                // Mission making commands
                "bwmf" => arma3::mission_making::get_bwmf::run(&ctx, &interaction).await,
                "upload" => arma3::mission_making::upload_mission::run(&ctx, &interaction).await,
                // // Recruitment commands
                // "handbook" => recruitment::handbook::run(&ctx, &interaction).await,
                // "orientation" => recruitment::request_orientation::run(&ctx, &interaction).await,
                // // Staff commands
                // "armaserver" => staff::armaserver::run(&ctx, &interaction).await,
                // "rpt" => staff::get_rpt::run(&ctx, &interaction).await,
                // "serverstatus" => staff::serverstatus::run(&ctx, &interaction).await,
                // "update_mods" => staff::update_mods::run(&ctx, &interaction).await,
                // "update_servers" => staff::update_servers::run(&ctx, &interaction).await,
                // // Users management not implemented
                // "register" => users::register::run(&ctx, &interaction).await,
                // "update" => users::update::run(&ctx, &command).await,
                // "user_delete" => users::delete::run(&ctx, &command).await,
                _ => Err(PotatoBotError::Command(
                    CommandError::CannotFindSlashCommand(),
                )),
            };
            info!("Executed command interaction: {:#?}", interaction.data.name);
            info!("Returned: {:?}", output)
        }
    }

    async fn ready(&self, ctx: Context, ready: Ready) {
        info!("{} is connected!", ready.user.name);

        let commands = GuildId::new(*GUILD_ID)
            .set_commands(
                &ctx.http,
                vec![
                    // Helper commands
                    community::docs::register(),
                    community::help::register(),
                    community::issue::register(),
                    community::sessiontime::register(),
                    // Arma 3
                    arma3::batman::register(),
                    arma3::html::register(),
                    arma3::leadership_feedback::register(),
                    // Mission making commands
                    arma3::mission_making::get_bwmf::register(),
                    arma3::mission_making::upload_mission::register(),
                    // Recruitment commands
                    recruitment::handbook::register(),
                    recruitment::request_orientation::register(),
                    // Staff commands
                    staff::armaserver::register(),
                    staff::get_rpt::register(),
                    staff::serverstatus::register(),
                    staff::update_mods::register(),
                    staff::update_servers::register(),
                    // User Commands
                    // users::register::register(),
                    // users::update::register(),
                    // users::delete::register(),
                ],
            )
            .await;

        info!(
            "I now have the following guild slash commands: {:#?}",
            commands
        );
    }
}
