use crate::prelude::*;

#[derive(Serialize)]
struct TemplateInputs {
    sustains: String,
    improves: String,
    overall: String,
}

impl TemplateInputs {
    // Function to create a HashMap from the struct
    fn to_map(&self) -> HashMap<String, String> {
        let mut map = HashMap::new();
        map.insert("sustains".to_string(), self.sustains.clone());
        map.insert("improves".to_string(), self.improves.clone());
        map.insert("overall".to_string(), self.overall.clone());
        map
    }
    fn new(inputs: Vec<&ActionRowComponent>) -> TemplateInputs {
        let (mut sustain, mut improve, mut overall) = (None, None, None);
        for input in inputs.iter() {
            match input {
                InputText(input) if input.custom_id == "sustains" => {
                    sustain = input.value.clone();
                }
                InputText(input) if input.custom_id == "improves" => {
                    improve = input.value.clone();
                }
                InputText(input) if input.custom_id == "overall" => {
                    overall = input.value.clone();
                }
                _ => error!("No input collected"),
            }
        }
        TemplateInputs {
            sustains: sustain.unwrap(),
            improves: improve.unwrap(),
            overall: overall.unwrap(),
        }
    }
}

fn read_file_to_string(file_path: &str) -> Result<String, Box<dyn Error>> {
    // Open the file
    let mut file = File::open(file_path)?;

    // Read the file's contents into a string
    let mut contents = String::new();
    file.read_to_string(&mut contents)?;

    Ok(contents)
}

pub async fn run(ctx: &Context, command: &CommandInteraction) -> Result<(), SerenityError> {
    let sustain_input = CreateInputText::new(InputTextStyle::Paragraph, "Sustains", "sustains")
        .required(true)
        .placeholder("What did they do well and should keep doing going forward?");
    let improve_input = CreateInputText::new(InputTextStyle::Paragraph, "Improves", "improves")
        .required(true)
        .placeholder("What could they do better next time?");
    let overall_input = CreateInputText::new(InputTextStyle::Paragraph, "Overall", "overall")
        .required(true)
        .placeholder("Overall how do you summarize their performance?");

    let modal = CreateModal::new("new_feedback", "Create new Feedback").components(vec![
        CreateActionRow::InputText(sustain_input),
        CreateActionRow::InputText(improve_input),
        CreateActionRow::InputText(overall_input),
    ]);

    match command
        .create_response(
            &ctx.http,
            serenity::builder::CreateInteractionResponse::Modal(modal),
        )
        .await
    {
        Ok(()) => info!("Creating new feedback"),
        Err(error) => error!("{:#?}", error),
    }

    let collector = ModalInteractionCollector::new(ctx)
        .filter(|int| int.data.custom_id == "new_feedback")
        .timeout(std::time::Duration::from_secs(600))
        .stream();

    let _ = collector.then(|input| async move {
        let inputs: Vec<_> = input
            .data
            .components
            .iter()
            .flat_map(|a| a.components.iter())
            .collect();

        let template_input = TemplateInputs::new(inputs);

        match input
            .create_response(
                &ctx.http,
                CreateInteractionResponse::Defer(CreateInteractionResponseMessage::new()),
            )
            .await
        {
            Ok(()) => info!("Finished creating feedback template"),
            Err(error) => error!("Failed: {}", error),
        }

        let template_contents = read_file_to_string("./templates/leadership_feedback");
        let filled_template = template_fill!(&template_contents.unwrap(), template_input.to_map());

        let embed = CreateEmbed::new()
            .title(format!("Feedback Template for {}", &command.user.name))
            .description(filled_template);

        if let Err(why) = command
            .create_followup(
                &ctx.http,
                CreateInteractionResponseFollowup::new()
                    .add_embed(embed)
                    .ephemeral(true),
            )
            .await
        {
            error!("Unable to create message response: {}", why);
        }
    });
    Ok(())
}

pub fn register() -> CreateCommand {
    CreateCommand::new("leadership_feedback").description("Provide leadership feedback to a member")
}
