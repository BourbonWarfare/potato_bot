use crate::backend::response::{Response, login_bot::Request as LoginBotRequest, RequestTrait};

pub struct Session {
    pub token: String,
    pub session_token: Option<String>,
}

impl Session {
    pub fn new(token: String) -> Self {
        Session {
            token,
            session_token: None
        }
    }

    pub async fn refresh_token(&mut self) -> Result<(), u16> {
        match (LoginBotRequest {
            bot_token: self.token.clone(),
        }.send(None).await) {
            Response::Success(response) => {
                self.session_token = Some(response.session_token);
            },
            Response::Error(status, message) => {
                tracing::error!("Failed to refresh token: {} - {}", status, message);
                return Err(status);
            }
        };
        Ok(())
    }
}