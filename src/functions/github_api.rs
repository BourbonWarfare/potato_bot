use log::info;

pub async fn create_issue(
    project_name: &str,
    title: &str,
    description: &str,
) -> Result<String, Box<dyn std::error::Error + Send + Sync>> {

    let owner = std::env::var("GITHUB_OWNER").unwrap();
    let octocrab = octocrab::Octocrab::builder()
        .personal_token(std::env::var("GITHUB_TOKEN").unwrap())
        .build()?;
    
    let response = octocrab.issues(owner, project_name).create(title)
        // Optional Parameters
        .body(description)
        // Send the request
        .send()
        .await?;

    let url = response.html_url.to_string();

    info!("GitHub API used to create issue: {}
            With the title: {}
            URL: {}",
        response.id,
        response.title,
        response.html_url
        );

    Ok(url)
}
