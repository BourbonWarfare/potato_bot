use crate::prelude::*;

pub async fn run(ctx: &Context, command: &CommandInteraction) -> Result<(), SerenityError> {
    let options = command.data.options();

    if let Some(ResolvedOption {
        value: ResolvedValue::String(commandname),
        ..
    }) = options.first()
    {
        let title = format!("Create new issue for {:#?}", &commandname);
        let modal = CreateQuickModal::new(title)
            .timeout(std::time::Duration::from_secs(600))
            .short_field("Issue Title")
            .paragraph_field("Issue Description");

        let response = command.quick_modal(ctx, modal).await?.unwrap();

        let inputs = response.inputs;
        let (title, description) = (&inputs[0], &inputs[1]);
        info!("title = {:#?}, description = {:#?}", title, description);

        let mut _issues_url = String::new();
        let mut _project = String::new();
        match *commandname {
            "potato" => {
                _project = "POTATO".to_string();
                _issues_url = "https://github.com/BourbonWarfare/POTATO/issues".to_string();
            }
            "potbot" => {
                _project = "potato_bot".to_string();
                _issues_url = "https://github.com/BourbonWarfare/potato_bot/issues".to_string();
            }
            "bwmf" => {
                _project = "bwmf".to_string();
                _issues_url = "https://github.com/BourbonWarfare/bwmf/issues".to_string();
            }
            _ => {
                error!("Shouldn't get here. Something went wrong'");
                _project = "POTATO".to_string();
                _issues_url = "https://github.com/BourbonWarfare/POTATO/issues".to_string();
            }
        };

        let url = functions::github_api::create_issue(&_project, &title, &description).await;

        let r_title = format!("Created new issue for {:#?}", &options.get(0));
        let embed = CreateEmbed::new()
            .title(r_title)
            .description(format!(
                "Your new issue can be viewed using the following link
                                {}
                                or but clicking the title of this message.
    
                                All {} issues can be viewed here:
                                {}
                                ",
                &url.as_ref().unwrap(),
                &commandname,
                _issues_url
            ))
            .url(&url.unwrap());

        command
            .create_response(
                &ctx.http,
                CreateInteractionResponse::Message(
                    CreateInteractionResponseMessage::new()
                        .embed(embed)
                        .ephemeral(true),
                ),
            )
            .await
    } else {
        command
            .create_response(
                &ctx.http,
                CreateInteractionResponse::Message(
                    CreateInteractionResponseMessage::new()
                        .content("No valid server provided")
                        .ephemeral(false),
                ),
            )
            .await
    }
}

pub fn register() -> CreateCommand {
    CreateCommand::new("issue")
        .description("Create a new issue for a given project")
        .add_option(
            CreateCommandOption::new(
                CommandOptionType::String,
                "issue",
                "What system does this issue pertain to.",
            )
            .required(true)
            .add_string_choice("Issue is with POTATO", "potato")
            .add_string_choice("Issue is with POTBOT", "potbot")
            .add_string_choice("Issue is with bwmf", "bwmf"),
        )
}
