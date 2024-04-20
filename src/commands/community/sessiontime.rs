use crate::prelude::*;

fn next_session(time: DateTime<Local>) -> PotatoResult<DateTime<Local>> {
    let session_time_today = Local
        .with_ymd_and_hms(
            time.year(),
            time.month(),
            time.day(),
            CONFIG.local_session_time,
            0,
            0,
        )
        .unwrap();
    let weekday_num = time.weekday().num_days_from_sunday();

    // Check if weekday given is after wednesday
    match weekday_num {
        0 => {
            if time > session_time_today {
                Ok(session_time_today + chrono::Duration::days(3 - weekday_num as i64))
            } else {
                Ok(session_time_today)
            }
        }
        1 | 2 => Ok(session_time_today + chrono::Duration::days(3 - weekday_num as i64)),
        3 => {
            if time > session_time_today {
                Ok(session_time_today + chrono::Duration::days(7 - weekday_num as i64))
            } else {
                Ok(session_time_today)
            }
        }
        4 | 5 | 6 => Ok(session_time_today + chrono::Duration::days(7 - weekday_num as i64)),
        _ => {
            error!("weekday_num = {} is outside of week", weekday_num);
            Err(PotatoError::Session(SessionError::WeekdayOutsideOfRange))
        }
    }
}

fn relative_time(relative: f64) -> PotatoResult<DateTime<Local>> {
    let session_time_today = Local
        .with_ymd_and_hms(2022, 1, 1, CONFIG.local_session_time, 0, 0)
        .unwrap();
    let seconds: i64 = (relative * 3600.0) as i64;
    Ok(session_time_today + chrono::Duration::seconds(seconds))
}

pub async fn run(ctx: &Context, interaction: &CommandInteraction) -> PotatoBotResult {
    let content = match get_option!(&interaction.data, "time", Number) {
        Ok(value) => {
            format!(
                "The requested time relative to session time <t:{}:t> [**{}**] is:\n**<t:{}:t>**",
                next_session(Local::now()).unwrap().timestamp(),
                value.to_string(),
                relative_time(value).unwrap().timestamp()
            )
        }
        _ => {
            format!(
                "Next Session will be:\n**<t:{0}:F>**\n*Roughly* <t:{0}:R>",
                next_session(Local::now()).unwrap().timestamp()
            )
        }
    };

    let embed = CreateEmbed::new()
        .title("🕓 Session Time Helper")
        .description(content)
        .colour(0xf31616);

    if let Err(e) = create_response_embed!(ctx, interaction, embed, true) {
        let _ = PotatoBotError::Discord(e)
            .send_error_response(ctx, interaction)
            .await;
    };

    Ok(())
}

pub fn register() -> CreateCommand {
    CreateCommand::new("sessiontime")
        .description("Calculate your local time relative to session time")
        .add_option(
            CreateCommandOption::new(
                CommandOptionType::Number,
                "time",
                "Relative time in hours. Can be negative and/or decimal",
            )
            .required(false),
        )
}
