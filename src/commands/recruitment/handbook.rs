use serenity::{
    all::{CommandInteraction, CommandOptionType, ResolvedOption, ResolvedValue},
    builder::{
        CreateCommand, CreateCommandOption, CreateEmbed, CreateInteractionResponse,
        CreateInteractionResponseMessage,
    },
    prelude::*,
};
use tracing::{error, info};

pub async fn run(ctx: &Context, command: &CommandInteraction) -> Result<(), SerenityError> {
    let options = command.data.options();

    let url = if let Some(ResolvedOption {
        value: ResolvedValue::String(handbook),
        ..
    }) = options.first()
    {
        info!("Getting link for handbook: {}", handbook);
        let out = match *handbook {
            "recruit" => "https://docs.bourbonwarfare.com/wiki/welcome-to-bw/recruit-handbook",
            "member" => "https://forums.bourbonwarfare.com/viewtopic.php?t=579",
            _ => {
                error!("No handbook selected");
                "https://docs.bourbonwarfare.com/wiki/"
            }
        };
        out
    } else {
        error!("No handbook selected");
        "https://docs.bourbonwarfare.com/wiki/"
    };

    let embed = CreateEmbed::new()
        .title("📓 CLICK HERE to open handbook")
        .description(
            "Handbooks and other useful information can be found on our website:
        https://docs.bourbonwarfare.com/wiki/",
        )
        .url(url);

    command
        .create_response(
            &ctx.http,
            CreateInteractionResponse::Message(
                CreateInteractionResponseMessage::new()
                    .embed(embed)
                    .ephemeral(true),
            ),
        )
        .await
}

pub fn register() -> CreateCommand {
    CreateCommand::new("handbook")
        .description("Links to our handbooks.")
        .add_option(
            CreateCommandOption::new(
                CommandOptionType::String,
                "handbook",
                "Select which handbook",
            )
            .required(true)
            .add_string_choice("📘 Recruit Handbook 😕", "recruit")
            .add_string_choice("📗 Member Handbook 🔫", "member"),
        )
}
