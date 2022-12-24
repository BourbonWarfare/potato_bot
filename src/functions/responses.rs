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
        _ => embed
            .title(content),
    };
    embed
}
