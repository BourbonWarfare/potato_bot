use serde::{ Serialize, Deserialize };
use reqwest::StatusCode;

pub enum Response<T> {
    Success(T),
    Error(u16, String),
}

pub trait RequestTrait<ResponseType>: Serialize where Self: Sized {
    fn api_url(&self) -> String;
    async fn send(self, token: Option<String>) -> Response<ResponseType> where for<'a> ResponseType: Deserialize<'a> {
        let backend_url = std::env::var("POTATO_BACKEND_URL")
            .expect("POTATO_BACKEND_URL environment variable is not set");
        let client = reqwest::Client::builder().danger_accept_invalid_certs(true).build().unwrap();
        let url = format!("{}{}", backend_url, self.api_url());

        let mut request = client.post(&url).json(&self);
        if let Some(token) = token {
            request = request.bearer_auth(token);
        }

        let response = request.send()
            .await
            .map_err(|e| Response::Error(
                e.status().or(Some(StatusCode::INTERNAL_SERVER_ERROR)).unwrap().as_u16(),
                e.to_string()
            ));
        if let Err(e) = response {
            return e;
        }
        // we cant directly unwrap the response because it doesnt implement `Debug` trait
        // id rather not make that a requirement for the `ResponseType`
        let Ok(response) = response else { unreachable!("Response should not be an error here") };

        let response = response.json::<ResponseType>().await;
        if let Err(e) = response {
            return Response::Error(
                e.status().map(|e| e.as_u16()).or(Some(0)).unwrap(),
                e.to_string()
            );
        }
        let response = response.unwrap();

        Response::Success(response)
    }
}

pub mod login_bot {
    use super::RequestTrait;
    use serde::{ Serialize, Deserialize };

    #[derive(Serialize)]
    pub struct Request {
        pub bot_token: String,
    }

    #[derive(Deserialize)]
    pub struct Response {
        pub session_token: String,
        #[allow(dead_code)]
        pub expire_time: String
    }

    impl RequestTrait<Response> for Request {
        fn api_url(&self) -> String {
            "/api/v1/users/auth/bot".to_string()
        }
    }
}

pub mod mission_upload {
    use std::collections::HashMap;

    use super::RequestTrait;
    use serde::{ Serialize, Deserialize };

    #[derive(Clone, Serialize)]
    pub struct Request {
        #[serde(skip_serializing)]
        pub location: String,
        pub pbo_path: String,
        pub changelog: HashMap<String, String>,
    }

    #[derive(Deserialize)]
    pub struct Response {
    }

    impl RequestTrait<Response> for Request {
        fn api_url(&self) -> String {
            format!("/api/v1/missions/upload/{}", self.location)
        }
    }
}