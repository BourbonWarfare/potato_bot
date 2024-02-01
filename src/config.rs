use serde::Deserialize;
use std::env;
use std::fs;
use toml;
use tracing::info;

#[derive(Debug, Deserialize)]
pub struct Config {
    pub locations: Vec<String>,
    pub local_session_time: u32,
    pub servers: Vec<A3ServerConfig>,
    pub mods: Vec<ModsList>,
}

#[derive(Debug, Deserialize)]
pub struct A3ServerConfig {
    pub name: String,
    pub name_pretty: String,
    pub port: u16,
    pub location: String,
    pub hc: u32,
    pub mods: Option<Vec<ModsList>>,
    pub password: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct ModsList {
    pub name: String,
    pub list: Vec<(String, u32)>,
}

pub fn get() -> Config {
    let config_location = env::var("ARMA_SERVERS_CONFIG")
        .expect("Env not set")
        .to_string();
    let toml_string = fs::read_to_string(config_location).expect("unable to read config file");
    let config: Config = toml::from_str(&toml_string).unwrap();
    info!("Config: {:?}", config);
    config
}
