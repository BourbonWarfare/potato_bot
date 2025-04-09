use serenity::http::Http;
use std::{mem::MaybeUninit, sync::Arc};

pub struct BotCache();

static mut SINGLETON: MaybeUninit<Arc<Http>> = MaybeUninit::uninit();

impl BotCache {
    /// Gets a reference to the Bot cache and http
    ///
    /// # Panics
    ///
    /// Panics if the bot does not exists
    pub fn get() -> Arc<Http> {
        #[allow(static_mut_refs)]
        unsafe {
            SINGLETON.assume_init_ref().clone()
        }
    }

    /// Initializes the Bot cache and http
    pub fn init(bot: Arc<Http>) {
        unsafe {
            SINGLETON = MaybeUninit::new(bot);
        }
    }
}
