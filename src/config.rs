use serde::Deserialize;
use std::env;
use std::fs;
use toml;

#[allow(dead_code)]
#[derive(Debug, Deserialize)]
pub struct Config {
    pub locations: Vec<String>,
    pub local_session_time: u32,
    pub timezone: String,
    pub servers: Vec<A3ServerConfig>,
    pub master_mod_list: Vec<Mod>,
    pub mods: Vec<ModsList>,
}

#[allow(dead_code)]
#[derive(Debug, Deserialize)]
pub struct A3ServerConfig {
    pub name: String,
    pub name_pretty: String,
    pub port: u16,
    pub location: String,
    pub hc: u32,
    pub auto_start: bool,
    pub modlist: Option<String>,
    pub password: Option<String>,
    pub cron_job: Option<CronJob>,
}

#[allow(dead_code)]
#[derive(Debug, Deserialize)]
pub struct CronJob {
    pub cron: String,
    pub action: String,
}

#[allow(dead_code)]
#[derive(Debug, Deserialize)]
pub struct ModsList {
    pub name: String,
    pub list: Vec<String>,
}

#[allow(dead_code)]
#[derive(Debug, Deserialize)]
pub struct Mod {
    pub name: String,
    pub id: u32,
    pub auto_update: bool,
    pub optional: bool,
}

pub fn get() -> Config {
    let config_location = env::var("ARMA_SERVERS_CONFIG")
        .expect("Env not set")
        .to_string();
    let toml_string = fs::read_to_string(config_location).expect("unable to read config file");
    let config: Config = toml::from_str(&toml_string).unwrap();
    config
}
