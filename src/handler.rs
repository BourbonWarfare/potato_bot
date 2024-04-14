use crate::prelude::*;

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
                "docs" => community::docs::run(&ctx, &command).await,
                "help" => community::help::run(&ctx, &command).await,
                "issue" => community::issue::run(&ctx, &command).await,
                "sessiontime" => community::sessiontime::run(&ctx, &command).await,
                // Arma 3 Commands
                "html" => arma3::html::run(&ctx, &command).await,
                "imbatman" => arma3::batman::run(&ctx, &command).await,
                "leadership_feedback" => arma3::leadership_feedback::run(&ctx, &command).await,
                // Mission making commands
                "bwmf" => arma3::mission_making::get_bwmf::run(&ctx, &command).await,
                "upload" => arma3::mission_making::upload_mission::run(&ctx, &command).await,
                // Recruitment commands
                "handbook" => recruitment::handbook::run(&ctx, &command).await,
                "orientation" => recruitment::request_orientation::run(&ctx, &command).await,
                // Staff commands
                "armaserver" => staff::armaserver::run(&ctx, &command).await,
                "rpt" => staff::get_rpt::run(&ctx, &command).await,
                "serverstatus" => staff::serverstatus::run(&ctx, &command).await,
                "update_mods" => staff::update_mods::run(&ctx, &command).await,
                "update_servers" => staff::update_servers::run(&ctx, &command).await,
                // Users management
                "register" => users::register::run(&ctx, &command).await,
                "update" => users::update::run(&ctx, &command).await,
                "delete" => users::delete::run(&ctx, &command).await,
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
                    users::register::register(),
                    users::update::register(),
                    users::delete::register(),
                ],
            )
            .await;

        info!(
            "I now have the following guild slash commands: {:#?}",
            commands
        );
    }
}
