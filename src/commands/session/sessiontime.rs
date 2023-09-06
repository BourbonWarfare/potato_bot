use chrono::{DateTime, Duration, Utc, Datelike, TimeZone};

use log::error;

use serenity::{
    builder::{CreateApplicationCommand, CreateEmbed},
    model::prelude::command::CommandOptionType,
    model::prelude::interaction::{
        application_command::{
            ApplicationCommandInteraction,
            CommandDataOption, 
            CommandDataOptionValue
        },
        InteractionResponseType},
    prelude::*
};

fn next_session(time: DateTime<Utc>) -> DateTime<Utc> {
    let session_time_today = Utc.with_ymd_and_hms(time.year(), time.month(), time.day(), 0, 0, 0).unwrap();
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
        1 | 2 => {
            session_time_today + Duration::days(3 - weekday_num as i64)
        }
        3 => {
            if time > session_time_today {
                session_time_today + Duration::days(7 - weekday_num as i64)
            } else {
                session_time_today 
            }
        }
        4 | 5 | 6 => {
            session_time_today + Duration::days(7 - weekday_num as i64)
        }
        _ => {
            error!("weekday_num = {} is outside of week", weekday_num);
            session_time_today
        }
    }
}

fn relative_time(relative: f64) -> DateTime<Utc> {
    let session_time_today = Utc.with_ymd_and_hms(2022, 1, 1, 0, 0, 0).unwrap();
    let seconds: i64 = (relative * 3600.0) as i64;
    session_time_today + Duration::seconds(seconds)
}

pub async fn run(
    ctx: &Context,
    command: &ApplicationCommandInteraction,
    options: &[CommandDataOption]
) -> Result<(), SerenityError> {

    let option = options.get(0);
    let local: DateTime<Utc> = Utc::now();
    let next_session: DateTime<Utc> = next_session(local);

    let content = if let Some(command_data_option) = option {
        if let Some(CommandDataOptionValue::Number(value)) = command_data_option.resolved { 
            let relative_time = relative_time(value);
            format!("The requested time relative to session time
                <t:{}:t> [**{}**] is:

                **<t:{}:t>**",
                next_session.timestamp(),
                value.to_string(),
                relative_time.timestamp())
        } else {
            error!("Something went horribly wrong");
            "Something went horribly wrong".to_string()
        }
    } else {
        format!("Next Session will be:

        **<t:{0}:F>**

        *Roughly* <t:{0}:R>
        ", next_session.timestamp())
    };
    
    let mut embed = CreateEmbed::default();

    embed
        .title("🕓 Session Time Helper")
        .description(content)
        .colour(0xf31616);

    command
        .create_interaction_response(&ctx.http, |response| {
            response
                .kind(InteractionResponseType::ChannelMessageWithSource)
                .interaction_response_data(|message| {
                    message
                        .add_embed(embed)
                        .ephemeral(false)
                })
        })
        .await
}

pub fn register(command: &mut CreateApplicationCommand) -> &mut CreateApplicationCommand {
    command
        .name("sessiontime")
        .description("Calculate your local time relative to session time")
        .create_option(|option| {
            option
                .name("time")
                .description("Relative time in hours. Can be negative and/or decimal")
                .kind(CommandOptionType::Number)
                .required(false)
        })
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn session_test() {
        assert_eq!(next_session(
                Utc.with_ymd_and_hms(2022,12,18,12,0,0).unwrap()),
                Utc.with_ymd_and_hms(2022,12,19,1,0,0).unwrap()
                );
        assert_eq!(next_session(
                Utc.with_ymd_and_hms(2022,12,13,12,0,0).unwrap()),
                Utc.with_ymd_and_hms(2022,12,15,1,0,0).unwrap()
                );
        assert_eq!(next_session(
                Utc.with_ymd_and_hms(2022,12,15,0,10,0).unwrap()),
                Utc.with_ymd_and_hms(2022,12,15,1,0,0).unwrap()
                );
        assert_eq!(next_session(
                Utc.with_ymd_and_hms(2022,12,15,12,0,0).unwrap()),
                Utc.with_ymd_and_hms(2022,12,19,1,0,0).unwrap()
                );
        assert_eq!(next_session(
                Utc.with_ymd_and_hms(2022,12,19,0,10,0).unwrap()),
                Utc.with_ymd_and_hms(2022,12,19,1,0,0).unwrap()
                );
    }
}
