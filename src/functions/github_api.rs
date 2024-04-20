use crate::prelude::*;

pub async fn create_issue(
    project_name: &str,
    title: &str,
    description: &str,
) -> Result<String, Box<dyn std::error::Error + Send + Sync>> {
    let octocrab = octocrab::Octocrab::builder()
        .personal_token(GITHUB_TOKEN.to_string())
        .build()?;

    let response = octocrab
        .issues(GITHUB_OWNER.to_string(), project_name)
        .create(title)
        // Optional Parameters
        .body(description)
        // Send the request
        .send()
        .await?;

    let url = response.html_url.to_string();

    info!(
        "GitHub API used to create issue: {}
            With the title: {}
            URL: {}",
        response.id, response.title, response.html_url
    );

    Ok(url)
}
