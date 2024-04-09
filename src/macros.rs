use serenity::all::{CommandData, CommandDataOptionValue};

pub fn _get_option<'a>(command: &'a CommandData, name: &str) -> Option<&'a CommandDataOptionValue> {
    let option = command.options.iter().find(|option| option.name == name)?;
    Some(&option.value)
}

#[macro_export]
macro_rules! get_option {
    ($data:expr, $name:expr, $typ:ident) => {
        match $crate::macros::_get_option($data, $name) {
            Some(CommandDataOptionValue::$typ(data)) => Some(data),
            _ => None,
        }
    };
}

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
            Payload::Text(str) => {
                info!("Successfully sent command to PSM");
                crate::socket::Response::new(true, str)
            }
            Payload::Binary(_) => {
                error!("Error sending message to PSM");
                crate::socket::Response::new(
                    false,
                    vec![serde_json::json!(["error", "Error recieved from socket"])],
                )
            }
            _ => panic!("Unable to parse the callback"),
        }
    };
}

#[macro_export]
macro_rules! emit {
    ($json:expr, $target:expr) => {
        crate::SOCKET
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
        crate::SOCKET
            .get()
            .expect("Unable to get socket")
            .emit_with_ack(
                $target,
                $json,
                std::time::Duration::from_secs(60 * 3),
                $callback,
            )
            .await
            .unwrap()
    };
}

#[macro_export]
macro_rules! sent_to_server {
    ($ctx:expr, $command:expr) => {
        $command
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
            .await?;
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
                        .embed($embed)
                        .ephemeral($ephemeral),
                ),
            )
            .await?;
    };
}
