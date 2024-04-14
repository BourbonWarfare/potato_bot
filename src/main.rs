use potato_bot::start_bot;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    start_bot().await;
    Ok(())
}
