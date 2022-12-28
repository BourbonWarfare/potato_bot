use serenity::builder::CreateEmbed;

pub fn generate_embed<'a>(
    command: &str,
    content: String,
) -> CreateEmbed {
    let mut embed = CreateEmbed::default();
    match command {
        "sessiontime" => embed
            .title("🕓 Session Time Helper")
            .description(content)
            .colour(0xf31616),
        "bwmf" => embed
            .title("📂 CLICK HERE to download")
            .description("Or visit the GitHub:
                https://github.com/BourbonWarfare/bwmf")
            .url(content),
        "handbook" => embed
            .title("📓 CLICK HERE to open handbook")
            .description("Handbooks and other useful information can be found on our website:
            https://forums.bourbonwarfare.com/index.php")
            .url(content),
        _ => embed
            .title(content),
    };
    embed
}

