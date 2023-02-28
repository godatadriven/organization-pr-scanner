import azure.functions as func

from dailymessage.daily_slack_message import send_daily_slack_message
from utils.filter import load_jsonl_string_into_df


def main(prsStream: func.InputStream, projectsIn: str, contributorsIn: str) -> None:
    prs = load_jsonl_string_into_df(prsStream.read().decode("utf-8"))
    projects = load_jsonl_string_into_df(projectsIn)
    contributors = load_jsonl_string_into_df(contributorsIn)

    send_daily_slack_message(prs, projects, contributors)
