import os
from datetime import date, datetime, timedelta
from typing import Dict

import pandas as pd
from slack_bolt import App
from slack_sdk.errors import SlackApiError

from utils.filter import create_analysis_table


def send_messages(pull_requests: pd.DataFrame) -> None:
    """
    Send a templated message for each incoming pull request.
    """
    app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

    for _, pr in pull_requests.iterrows():
        message = build_message(pr)
        send_message(app, message)


def build_message(pr: Dict) -> str:
    """
    Create a templated message based on a the pull request data.
    """
    contributor = pr["contributor_name"]
    project = pr["project_name"]
    title = pr["pr_title"]
    closed_datetime = datetime.strptime(pr["closed_at"], "%Y-%m-%d %H:%M:%S")

    message = (
        f"Congratulations to {contributor} with a contribution on *{project}*, "
        f"titled _{title}_. It was merged on *{closed_datetime.date()}*."
    )
    return message


def send_message(app: App, message: str) -> None:
    """
    Send the templated message through Slack.
    """
    response = app.client.chat_postMessage(
        channel=os.environ.get("SLACK_CHANNEL"),
        text=message,
    )
    try:
        response.validate()
    except SlackApiError:
        assert False


def get_yesterdays_pull_requests(
    prs: pd.DataFrame, projects: pd.DataFrame, contributors: pd.DataFrame
) -> pd.DataFrame:
    today = date.today()
    yesterday = today - timedelta(days=1)

    yesterdays_pull_requests = create_analysis_table(
        prs,
        projects,
        contributors,
        minimum_stars=int(os.environ.get("MINIMUM_STARS")),
        start_date=yesterday,
        end_date=today,
    )

    return yesterdays_pull_requests


def send_daily_slack_message(
    pull_requests: pd.DataFrame, projects: pd.DataFrame, contributors: pd.DataFrame
) -> None:
    yesterdays_pull_requests = get_yesterdays_pull_requests(
        pull_requests, projects, contributors
    )
    send_messages(yesterdays_pull_requests)
