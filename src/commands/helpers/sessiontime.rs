use chrono::{DateTime, Datelike, Duration, Local, TimeZone};

use serenity::all::{ResolvedOption, ResolvedValue};
use tracing::error;

use serenity::{
    all::{CommandInteraction, CommandOptionType},
    builder::{
        CreateCommand, CreateCommandOption, CreateEmbed, CreateInteractionResponse,
        CreateInteractionResponseMessage,
    },
    prelude::*,
};

fn next_session(time: DateTime<Local>) -> DateTime<Local> {
    let session_time_today = Local
        .with_ymd_and_hms(time.year(), time.month(), time.day(), 1, 0, 0)
        .unwrap();
    let weekday_num = time.weekday().num_days_from_monday();

    // Check if weekday given is after wednesday
    match weekday_num {
        0 => {
            if time > session_time_today {
                session_time_today + Duration::days(3 - weekday_num as i64)
            } else {
                session_time_today
            }
        }
        1 | 2 => session_time_today + Duration::days(3 - weekday_num as i64),
        3 => {
            if time > session_time_today {
                session_time_today + Duration::days(7 - weekday_num as i64)
            } else {
                session_time_today
            }
        }
        4 | 5 | 6 => session_time_today + Duration::days(7 - weekday_num as i64),
        _ => {
            error!("weekday_num = {} is outside of week", weekday_num);
            session_time_today
        }
    }
}

fn relative_time(relative: f64) -> DateTime<Local> {
    let session_time_today = Local.with_ymd_and_hms(2022, 1, 1, 1, 20, 0).unwrap();
    let seconds: i64 = (relative * 3600.0) as i64;
    session_time_today + Duration::seconds(seconds)
}

pub async fn run(ctx: &Context, command: &CommandInteraction) -> Result<(), SerenityError> {
    let options = command.data.options();
    let local: DateTime<Local> = Local::now();
    let next_session: DateTime<Local> = next_session(local);

    let content = if let Some(ResolvedOption {
        value: ResolvedValue::Number(value),
        ..
    }) = options.first()
    {
        let relative_time = relative_time(*value);
        format!(
            "The requested time relative to session time
                <t:{}:t> [**{}**] is:

                **<t:{}:t>**",
            next_session.timestamp(),
            value.to_string(),
            relative_time.timestamp()
        )
    } else {
        format!(
            "Next Session will be:

        **<t:{0}:F>**

        *Roughly* <t:{0}:R>
        ",
            next_session.timestamp()
        )
    };

    let embed = CreateEmbed::new()
        .title("🕓 Session Time Helper")
        .description(content)
        .colour(0xf31616);

    command
        .create_response(
            &ctx.http,
            CreateInteractionResponse::Message(
                CreateInteractionResponseMessage::new()
                    .add_embed(embed)
                    .ephemeral(false),
            ),
        )
        .await
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

#[cfg(test)]
mod tests {

    use super::*;
    #[test]
    fn session_test() {
        assert_eq!(
            next_session(Local.with_ymd_and_hms(2022, 12, 18, 12, 0, 0).unwrap()),
            Local.with_ymd_and_hms(2022, 12, 19, 1, 0, 0).unwrap()
        );
        assert_eq!(
            next_session(Local.with_ymd_and_hms(2022, 12, 13, 12, 0, 0).unwrap()),
            Local.with_ymd_and_hms(2022, 12, 15, 1, 0, 0).unwrap()
        );
        assert_eq!(
            next_session(Local.with_ymd_and_hms(2022, 12, 15, 0, 10, 0).unwrap()),
            Local.with_ymd_and_hms(2022, 12, 15, 1, 0, 0).unwrap()
        );
        assert_eq!(
            next_session(Local.with_ymd_and_hms(2022, 12, 15, 12, 0, 0).unwrap()),
            Local.with_ymd_and_hms(2022, 12, 19, 1, 0, 0).unwrap()
        );
        assert_eq!(
            next_session(Local.with_ymd_and_hms(2022, 12, 19, 0, 10, 0).unwrap()),
            Local.with_ymd_and_hms(2022, 12, 19, 1, 0, 0).unwrap()
        );
    }
}
