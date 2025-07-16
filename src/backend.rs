use crate::backend::response::RequestTrait;
use std::time::Duration;
use exponential_backoff::Backoff;
use tokio::time::sleep;

mod response;
mod session;

pub struct Interface {
    session: session::Session,
}

impl Interface {
    pub fn new(bot_token: String) -> Self {
        Interface {
            session: session::Session::new(bot_token),
        }
    }

    pub async fn upload(
        &mut self,
        location: String,
        mission_path: String,
        changelog: std::collections::HashMap<String, String>,
    ) {
        if let None = self.session.session_token {
            if let Err(status) = self.session.refresh_token().await {
                tracing::error!("Failed to refresh session token: Status code {}. Can't upload mission.", status);
                return;
            }
        }

        let request = response::mission_upload::Request {
            location,
            mission_path,
            changelog,
        };

        for duration in Backoff::new(
            5, 
            Duration::from_millis(100),
            Duration::from_secs(5),
        ) {
            let response = request.clone().send(self.session.session_token.clone()).await;
            match response {
                response::Response::Success(_) => {
                    tracing::info!("Mission uploaded successfully.");
                    break
                },
                response::Response::Error(status, message) => {
                    tracing::error!("Failed to upload mission: {} - {}", status, message);
                    match status {
                        401 => {
                            tracing::error!("Session token expired. Refreshing session token.");
                            if let Err(status) = self.session.refresh_token().await {
                                tracing::error!("Failed to refresh session token: Status code {}. Can't upload mission.", status);
                                break;
                            } else {
                                tracing::info!("Session token refreshed successfully.");
                            }
                        },
                        403 => {
                            tracing::error!("Forbidden: You do not have permission to upload missions.");
                            break;
                        },
                        _ => {
                            tracing::error!("Unexpected error occurred: Status code {}", status);
                            break;
                        }
                    }
                }
            };
            sleep(duration.or(Some(Duration::from_millis(100))).unwrap()).await;
        }
    }
}