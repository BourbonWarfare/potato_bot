use crate::prelude::*;

fn get_target(target: String) -> Result<u64, Box<dyn Error>> {
    let id = match target.as_str() {
        "arma" => *ARMA_GENERAL_CHANNEL_ID,
        "member" => *MEMBER_CHANNEL_ID,
        "staff" => *STAFF_CHANNEL_ID,
        "admin" => *ADMIN_CHANNEL_ID,
        "tech" => *TECH_CHANNEL_ID,
        "recruit" => *RECRUITMENT_CHANNEL_ID,
        "bot" => *BOT_SPAM_CHANNEL_ID,
        "mod_update" => *MOD_UPDATE_CHANNEL_ID,
        _ => {
            error!("Not a valid target");
            0
        }
    };
    Ok(id)
}

pub async fn message(payload: Vec<Value>) -> PotatoBotResult {
    info!("Received message request: {:?}", payload);

    let request_contents: potato_socket::BotMessage = potato_socket::BotMessage::new(payload);

    let target = get_target(request_contents.channel).expect("Unable to get valid target channel");

    let channel_id = ChannelId::from(target);

    let response = channel_id
        .send_message(
            http::BotCache::get(),
            CreateMessage::new().content(request_contents.message),
        )
        .await;

    match response {
        Ok(_) => Ok(()),
        Err(e) => Err(PotatoBotError::Discord(DiscordError::CannotSendResponse(e))),
    }
}

pub async fn embed(payload: Vec<Value>) -> PotatoBotResult {
    info!("Received embed request: {:?}", payload);

    let request_contents: potato_socket::BotMessage = potato_socket::BotMessage::new(payload);

    let target = get_target(request_contents.channel).expect("Unable to get valid target channel");

    let channel_id = ChannelId::from(target);

    let title = if request_contents.title.is_some() {
        request_contents.title.unwrap()
    } else {
        panic!("Title is required for an embed")
    };

    let message = if request_contents.attachment.is_some() {
        let attachment = CreateAttachment::path(request_contents.attachment.unwrap())
            .await
            .expect("Unable to create attachment from path");
        CreateMessage::new().add_file(attachment)
    } else {
        CreateMessage::new()
    };

    let embed = CreateEmbed::new()
        .title(title)
        .description(request_contents.message);

    let f_embed = embed_generics!(embed, request_contents.origin.unwrap());
    let f_message = message.embed(f_embed);

    let response = channel_id
        .send_message(http::BotCache::get(), f_message)
        .await;

    match response {
        Ok(_) => Ok(()),
        Err(e) => Err(PotatoBotError::Discord(DiscordError::CannotSendResponse(e))),
    }
}

pub async fn scheduled_session_message(payload: Vec<Value>) -> PotatoBotResult {
    info!("Received embed request: {:?}", payload);

    // TODO: Include the extra fun stuff here that will link to the session aar id etc
    /* let _request_contents: Session =
    serde_json::from_str(payload.as_str()).expect("Unable to parse message"); */

    let title = format!("Session Time T-1 Hour");
    let description = "Today's session starts in one hour.
Make sure that you have updated your mods.";
    let content = format!("<@&{}> and <@&{}>", *MEMBER_ROLE_ID, *RECRUIT_ROLE_ID);

    let embed = CreateEmbed::new()
            .title(title)
            .description(description)
            .image("https://cdn.discordapp.com/attachments/285837079139844096/724897893315641404/unknown.png?ex=661e3145&is=660bbc45&hm=e9a36f7f7af1f853e0d2188ebabd63575609d89fa07536f620742974b38121d5&")
            .colour(Colour::from_rgb(239, 79, 10));
    let message = CreateMessage::new().content(content);
    let f_embed = embed_generics!(embed, "test");
    let f_message = message.embed(f_embed);
    let channel_id = ChannelId::from(
        get_target("arma".to_string()).expect("Unable to get valid target channel"),
    );
    let response = channel_id
        .send_message(http::BotCache::get(), f_message)
        .await;

    match response {
        Ok(_) => Ok(()),
        Err(e) => Err(PotatoBotError::Discord(DiscordError::CannotSendResponse(e))),
    }
}

pub async fn mod_update_message(payload: Vec<Value>) -> PotatoBotResult {
    info!("Received embed request: {:?}", payload);

    let request_contents: manage::Mod = manage::Mod::new(payload);

    let msg = format!(
        "# __**PSM arma3::manage::Mod update: {0}**__
[{0} Workshop Page](https://steamcommunity.com/sharedfiles/filedetails/?id={1})",
        request_contents.ws_name, request_contents.ws_id
    );

    for ws_mod in vec!["mod_update", "tech"] {
        let target = get_target(ws_mod.to_string()).expect("Unable to get valid target channel");

        let channel_id = ChannelId::from(target);

        let response = channel_id
            .send_message(http::BotCache::get(), CreateMessage::new().content(&msg))
            .await;

        match response {
            Ok(_) => Ok(()),
            Err(e) => Err(PotatoBotError::Discord(DiscordError::CannotSendResponse(e))),
        };
    }
    Ok(())
}
