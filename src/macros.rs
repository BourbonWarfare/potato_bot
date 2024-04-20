use crate::prelude::*;

#[macro_export]
macro_rules! confirm_action {
    ($msg:expr) => {
        serenity::builder::CreateMessage::new()
            .content($msg)
            .button(
                serenity::builder::CreateButton::new("confirm")
                    .style(serenity::model::application::ButtonStyle::Danger)
                    .label("Do it"),
            )
            .button(
                serenity::builder::CreateButton::new("cancel")
                    .style(serenity::model::application::ButtonStyle::Primary)
                    .label("Cancel"),
            )
    };
}

#[macro_export]
macro_rules! callback_and_response {
    ($payload:expr) => {
        match $payload {
            Payload::Text(_) => {
                info!("Recieved a valid response from PSM");
                true
            }
            _ => {
                error!("Error sending message to PSM");
                false
            }
        }
    };
}

#[macro_export]
macro_rules! emit {
    ($json:expr, $target:expr) => {
        crate::SOCKET_CLIENT
            .get()
            .expect("Unable to get socket")
            .emit($target, $json)
            .await
            .unwrap()
    };
}

#[macro_export]
macro_rules! emit_and_ack {
    ($json:expr, $target:expr, $callback:expr) => {
        crate::SOCKET_CLIENT
            .get()
            .expect("Unable to get socket")
            .emit_with_ack(
                $target,
                $json,
                std::time::Duration::from_secs(60 * 3),
                $callback,
            )
            .await
    };
}

#[macro_export]
macro_rules! sent_to_server {
    ($ctx:expr, $interaction:expr) => {
        let _ = $interaction
            .clone()
            .create_response(
                $ctx,
                CreateInteractionResponse::Message(
                    CreateInteractionResponseMessage::default()
                        .ephemeral(true)
                        .content("Message has been sent to server to execute command"),
                ),
            )
            .await;
    };
}

#[macro_export]
macro_rules! create_response_message {
    ($ctx:expr, $interaction:expr, $msg:expr, $ephemeral:expr) => {
        $interaction
            .create_response(
                $ctx,
                CreateInteractionResponse::Message(
                    CreateInteractionResponseMessage::new()
                        .content($msg)
                        .ephemeral($ephemeral),
                ),
            )
            .await
            .map_err(DiscordError::CannotSendResponse)
    };
}

#[macro_export]
macro_rules! create_response_embed {
    ($ctx:expr, $interaction:expr, $embed:expr, $ephemeral:expr) => {
        $interaction
            .create_response(
                $ctx,
                CreateInteractionResponse::Message(
                    CreateInteractionResponseMessage::new()
                        .embed(embed_generics!($embed, $interaction.data.name))
                        .ephemeral($ephemeral),
                ),
            )
            .await
            .map_err(DiscordError::CannotSendResponse)
    };
}

#[macro_export]
macro_rules! create_response_embed_attachment {
    ($ctx:expr, $interaction:expr, $embed:expr, $attachment:expr, $ephemeral:expr) => {
        $interaction
            .create_response(
                $ctx,
                CreateInteractionResponse::Message(
                    CreateInteractionResponseMessage::new()
                        .add_file($attachment)
                        .embed(embed_generics!($embed, $interaction.data.name))
                        .ephemeral($ephemeral),
                ),
            )
            .await
            .map_err(DiscordError::CannotSendResponse)
    };
}

#[macro_export]
macro_rules! create_defer_message {
    ($ctx:expr, $interaction:expr) => {
        $interaction
            .create_response(
                $ctx,
                CreateInteractionResponse::Defer(CreateInteractionResponseMessage::new()),
            )
            .await
            .map_err(DiscordError::CannotSendResponse)
    };
}

#[macro_export]
macro_rules! create_followup_embed {
    ($ctx:expr, $interaction:expr, $embed:expr, $ephemeral:expr) => {
        $interaction
            .create_followup(
                $ctx,
                CreateInteractionResponseFollowup::new()
                    .embed(embed_generics!($embed, $interaction.data.name)),
            )
            .await
            .map_err(DiscordError::CannotSendResponse)
    };
}

#[macro_export]
macro_rules! create_followup_embed_attachment {
    ($ctx:expr, $interaction:expr, $embed:expr, $attachment:expr, $ephemeral:expr) => {
        $interaction
            .create_followup(
                $ctx,
                CreateInteractionResponseFollowup::new()
                    .add_file($attachment)
                    .embed(embed_generics!($embed, $interaction.data.name)),
            )
            .await
            .map_err(DiscordError::CannotSendResponse)
    };
}

#[macro_export]
macro_rules! create_followup_message {
    ($ctx:expr, $interaction:expr, $msg:expr, $ephemeral:expr) => {
        $interaction
            .create_followup($ctx, CreateInteractionResponseFollowup::new().content($msg))
            .await
            .map_err(DiscordError::CannotSendResponse)
    };
}

#[macro_export]
macro_rules! create_acknowledge_response {
    ($ctx:expr, $interaction:expr) => {
        $interaction
            .create_response($ctx, CreateInteractionResponse::Acknowledge)
            .await
            .map_err(DiscordError::CannotSendResponse)
    };
}

#[macro_export]
macro_rules! interaction_successful {
    ($interaction:expr) => {
        Ok(format!(
            "Successfully completed /{} interaction",
            $interaction.data.name
        ))
    };
}

#[macro_export]
macro_rules! download_interaction_attachment {
    ($attachment:expr, $dest_path:expr, $ctx:expr, $interaction:expr) => {{
        let content = $attachment.download().await.unwrap().map_err(|e| {
            PotatoBotError::Command(CommandError::CannotDownloadAttachment(e))
                .send_error_response($ctx, $interaction)
        });
        let mut path = File::create($dest_path).await.map_err(|e| {
            PotatoBotError::PotatoError(PotatoError::System(SystemError::CannotCreateFileAtPath(e)))
                .send_error_response($ctx, $interaction)
        });
        path.unwrap().write_all(&content).await.map_err(|_| {
            PotatoBotError::Command(CommandError::CannotRetrieveAttachment)
                .send_error_response($ctx, $interaction)
        });
    }};
}

#[macro_export]
macro_rules! interaction_failed {
    ($error:expr, $ctx:expr, $interaction:expr) => {{
        let _ = $error.send_error_response($ctx, $interaction).await;
        Err($error)
    }};
}

#[macro_export]
macro_rules! embed_generics {
    ($embed:expr, $text:expr) => {
        $embed
            .footer(
                CreateEmbedFooter::new(format!("potato_bot {} command output", $text))
                    .icon_url("https://avatars.githubusercontent.com/u/16518830?s=200&v=4"),
            )
            .author(
                CreateEmbedAuthor::new("")
                    .url("https://github.com/BourbonWarfare/potato_bot")
                    .icon_url("https://avatars.githubusercontent.com/u/16518830?s=200&v=4"),
            )
    };
}

pub fn _get_option<'a>(
    command: &'a CommandData,
    name: &str,
) -> PotatoBotResult<CommandDataOptionValue> {
    match command
        .options
        .iter()
        .find(|option| option.name == name)
        .ok_or(PotatoBotError::Command(
            CommandError::CannotFindCommandOption,
        )) {
        Ok(o) => Ok(o.clone().value),
        Err(_) => Err(PotatoBotError::Command(
            CommandError::CannotRetrieveOptionValue,
        )),
    }
}

#[macro_export]
macro_rules! get_option {
    ($data:expr, $name:expr, $typ:ident) => {
        match $crate::macros::_get_option($data, $name) {
            Ok(CommandDataOptionValue::$typ(data)) => Ok(data),
            _ => Err(PotatoBotError::Command(
                CommandError::CannotRetrieveOptionValue,
            )),
        }
    };
}

pub fn _get_attachment<'a>(
    interaction: &'a CommandData,
    id: AttachmentId,
) -> PotatoBotResult<&Attachment> {
    interaction
        .resolved
        .attachments
        .get(&id)
        .ok_or(PotatoBotError::Command(
            CommandError::CannotRetrieveAttachment,
        ))
}

#[macro_export]
macro_rules! get_attachment_from_id {
    ($interaction:expr, $id:expr) => {
        $crate::macros::_get_attachment($interaction, $id)
    };
}

#[macro_export]
macro_rules! check_user_has_role {
    ($ctx:expr,$user:expr, $role_id:expr) => {
        $user
            .has_role(
                $ctx.clone().http,
                GuildId::new(*GUILD_ID),
                RoleId::new($role_id),
            )
            .await
    };
}

#[macro_export]
macro_rules! give_user_new_role {
    ($ctx:expr, $user:expr, $role_id:expr) => {
        $user
            .add_role($ctx.clone().http, RoleId::new($role_id))
            .await
    };
}

#[macro_export]
macro_rules! check_attachment_filetype {
    ($attachment:expr, $ext:expr) => {
        match $attachment.filename.contains($ext) {
            true => Ok($attachment),
            false => Err(PotatoBotError::Command(
                CommandError::InvalidAttachmentExtension($ext.to_string()),
            )),
        }
    };
}
