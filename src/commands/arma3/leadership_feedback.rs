use crate::prelude::*;

//TODO: Need to make this so that it is only possible to make this in the leadership threads
//TODO: Auto fill the remaining fields not in modal from thread and user info

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

pub async fn run(ctx: &Context, interaction: &CommandInteraction) -> PotatoBotResult<String> {
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

    match interaction
        .create_response(
            &ctx.http,
            serenity::builder::CreateInteractionResponse::Modal(modal),
        )
        .await
    {
        Ok(_) => {
            let mut collector = ModalInteractionCollector::new(ctx)
                .filter(|int| int.data.custom_id == "new_feedback")
                .timeout(std::time::Duration::from_secs(600))
                .stream();

            let modal_interation = collector.next().await.expect("I dunno");
            let _ = match create_acknowledge_response!(ctx, modal_interation) {
                Ok(_) => interaction_successful!(interaction),
                Err(e) => {
                    let err = PotatoBotError::Discord(e);
                    interaction_failed!(err, ctx, interaction)
                }
            };
            let inputs: Vec<_> = modal_interation
                .data
                .components
                .iter()
                .flat_map(|a| a.components.iter())
                .collect();

            let template_input = TemplateInputs::new(inputs);

            match fs::read_to_string("./templates/leadership_feedback") {
                Ok(template_contents) => {
                    let filled_template =
                        template_fill!(&template_contents, template_input.to_map());
                    let embed = CreateEmbed::new()
                        .title(format!("Feedback Template for {}", &interaction.user.name))
                        .description(filled_template);

                    match create_followup_embed!(ctx, interaction, embed, true) {
                        Ok(_) => interaction_successful!(interaction),
                        Err(e) => {
                            let err = PotatoBotError::Discord(e);
                            let _ = err.send_error_response(ctx, interaction).await;
                            interaction_failed!(err, ctx, interaction)
                        }
                    }
                }
                Err(_) => {
                    let err = PotatoBotError::PotatoError(PotatoError::System(
                        SystemError::CannotReadFileToString(),
                    ));
                    let _ = err.send_error_response(ctx, interaction).await;
                    Err(err)
                }
            }
        }
        Err(e) => {
            let err = PotatoBotError::Command(CommandError::UnableToCreateModal(e));
            let _ = err.send_error_response(ctx, interaction).await;
            Err(err)
        }
    }
}

pub fn register() -> CreateCommand {
    CreateCommand::new("leadership_feedback").description("Provide leadership feedback to a member")
}
