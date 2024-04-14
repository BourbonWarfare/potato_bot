use crate::prelude::*;

#[derive(Debug, Deserialize)]
pub struct Config {
    pub locations: Vec<String>,
    pub local_session_time: u32,
    pub timezone: String,
    pub log_path: String,
    pub cron_jobs: Option<Vec<CronJob>>,
    pub master_mod_list: Vec<Mod>,
    pub servers: Vec<A3ServerConfig>,
    pub mods: Vec<ModsList>,
}

impl Config {
    pub fn get_server(&self, name: &str) -> Option<&A3ServerConfig> {
        self.servers.iter().find(|s| s.name == name)
    }
}

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
    pub creatordlc: Option<Vec<String>>,
    pub cron_jobs: Option<Vec<CronJob>>,
}

#[derive(Debug, Deserialize)]
pub struct CronJob {
    pub action: String,
    pub cron: String,
}

#[derive(Debug, Deserialize)]
pub struct ModsList {
    pub name: String,
    pub list: Vec<String>,
}

#[derive(Debug, Deserialize, Clone)]
pub struct Mod {
    pub name: String,
    pub id: u32,
    pub auto_update: bool,
    pub optional: bool,
    pub server: bool,
    pub manual_install: bool,
    pub retry: u32,
}

pub fn get() -> Config {
    let config_location = env::var("ARMA_SERVERS_CONFIG")
        .expect("Env not set")
        .to_string();
    let toml_string = fs::read_to_string(config_location).expect("unable to read config file");
    let config: Config = toml::from_str(&toml_string).unwrap();
    config
}
