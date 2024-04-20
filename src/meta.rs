use crate::prelude::*;

lazy_static! {
    // Socket
    pub static ref SOCKET_CLIENT: OnceCell<rust_socketio::asynchronous::Client> = OnceCell::new();
    // General Discord
    pub static ref DISCORD_TOKEN: String = get_env_var!("discord_token");
    pub static ref GUILD_ID: u64 = get_env_var_u64!("guild_id");

    // Discord Channel IDs
    pub static ref ARMA_GENERAL_CHANNEL_ID: u64 = get_env_var_u64!("arma_general_channel_id");
    pub static ref MEMBER_CHANNEL_ID: u64 = get_env_var_u64!("member_channel_id");
    pub static ref STAFF_CHANNEL_ID: u64 = get_env_var_u64!("staff_channel_id");
    pub static ref ADMIN_CHANNEL_ID: u64 = get_env_var_u64!("admin_channel_id");
    pub static ref TECH_CHANNEL_ID: u64 = get_env_var_u64!("tech_channel_id");
    pub static ref RECRUITMENT_CHANNEL_ID: u64 = get_env_var_u64!("recruitment_channel_id");
    pub static ref BOT_SPAM_CHANNEL_ID: u64 = get_env_var_u64!("bot_spam_channel_id");
    pub static ref MOD_UPDATE_CHANNEL_ID: u64 = get_env_var_u64!("mod_update_channel_id");

    // Discord Role IDs
    pub static ref ORIENTATION_ROLE_ID: u64 = get_env_var_u64!("orientation_role_id");
    pub static ref AWAITING_ORIENTATION_ROLE_ID: u64 = get_env_var_u64!("awaiting_orientation_role_id");
    pub static ref RECRUIT_ROLE_ID: u64 = get_env_var_u64!("recruit_role_id");
    pub static ref MEMBER_ROLE_ID: u64 = get_env_var_u64!("member_role_id");
    pub static ref STAFF_ROLE_ID: u64 = get_env_var_u64!("staff_role_id");
    pub static ref TECH_STAFF_ROLE_ID: u64 = get_env_var_u64!("tech_staff_role_id");
    pub static ref ADMIN_ROLE_ID: u64 = get_env_var_u64!("admin_role_id");
    pub static ref MISSION_MAKER_ROLE_ID: u64 = get_env_var_u64!("mission_maker_role_id");
    pub static ref MISSION_TESTER_ROLE_ID: u64 = get_env_var_u64!("mission_tester_role_id");

    // Mod management
    pub static ref HTML_FILE_PATH: String = get_env_var!("html_file_path");
    pub static ref BAT_FILE_PATH: String = get_env_var!("bat_file_path");

    // Github
    pub static ref GITHUB_TOKEN: String = get_env_var!("github_token");
    pub static ref GITHUB_OWNER: String = get_env_var!("github_owner");

    // Reqwest
    pub static ref SERVER_MANGER_URL: String = get_env_var!("server_manger_url");

    // Maintainer Discord ID for mention
    pub static ref MAINTAINER_DISCORD_ID: String = get_env_var!("maintainer_discord_id");
}

pub fn init() {
    // Make sure that all lazy_statics are initialzied
    // From potato
    lazy_static::initialize(&MAINTAINER);
    lazy_static::initialize(&CONFIG);
    lazy_static::initialize(&SOCKET_CLIENT);
    lazy_static::initialize(&ARMA_BASE_DIR);
    lazy_static::initialize(&ARMA_MISSIONS_BASE_DIR);
    lazy_static::initialize(&CARGO_MANIFEST_DIR);
    lazy_static::initialize(&TEMPLATE_DIR);
    lazy_static::initialize(&DATABASE_URL);
    lazy_static::initialize(&DB);

    // Bot Specific
    // General Discord
    lazy_static::initialize(&MAINTAINER_DISCORD_ID);
    lazy_static::initialize(&DISCORD_TOKEN);
    lazy_static::initialize(&GUILD_ID);
    lazy_static::initialize(&ARMA_GENERAL_CHANNEL_ID);
    lazy_static::initialize(&MEMBER_CHANNEL_ID);
    lazy_static::initialize(&STAFF_CHANNEL_ID);
    lazy_static::initialize(&ADMIN_CHANNEL_ID);
    lazy_static::initialize(&TECH_CHANNEL_ID);
    lazy_static::initialize(&RECRUITMENT_CHANNEL_ID);
    lazy_static::initialize(&BOT_SPAM_CHANNEL_ID);
    lazy_static::initialize(&MOD_UPDATE_CHANNEL_ID);
    lazy_static::initialize(&ORIENTATION_ROLE_ID);
    lazy_static::initialize(&AWAITING_ORIENTATION_ROLE_ID);
    lazy_static::initialize(&RECRUIT_ROLE_ID);
    lazy_static::initialize(&MEMBER_ROLE_ID);
    lazy_static::initialize(&STAFF_ROLE_ID);
    lazy_static::initialize(&TECH_STAFF_ROLE_ID);
    lazy_static::initialize(&ADMIN_ROLE_ID);
    lazy_static::initialize(&MISSION_MAKER_ROLE_ID);
    lazy_static::initialize(&MISSION_TESTER_ROLE_ID);
    lazy_static::initialize(&HTML_FILE_PATH);
    lazy_static::initialize(&BAT_FILE_PATH);
    lazy_static::initialize(&GITHUB_TOKEN);
    lazy_static::initialize(&GITHUB_OWNER);
    lazy_static::initialize(&SERVER_MANGER_URL);
}
