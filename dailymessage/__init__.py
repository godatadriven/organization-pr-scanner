import logging
from datetime import datetime, timezone

import azure.functions as func

from dailymessage.daily_slack_message import send_daily_slack_message
from utils.filter import load_jsonl_string_into_df


def main(
    dailyTimer: func.TimerRequest, prsIn: str, projectsIn: str, contributorsIn: str
) -> None:
    utc_timestamp = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    if dailyTimer.past_due:
        logging.info("The timer is past due!")

    prs = load_jsonl_string_into_df(prsIn)
    projects = load_jsonl_string_into_df(projectsIn)
    contributors = load_jsonl_string_into_df(contributorsIn)

    send_daily_slack_message(prs, projects, contributors)
    logging.info("Python timer trigger function ran at %s", utc_timestamp)
