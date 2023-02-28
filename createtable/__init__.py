import logging
from datetime import datetime, timezone

import azure.functions as func

from createtable.create_monthly_table import create_monthly_table
from utils.filter import load_jsonl_string_into_df


def main(
    monthlyTimer: func.TimerRequest,
    prsIn: str,
    projectsIn: str,
    contributorsIn: str,
    tableOut: func.Out[bytes],
) -> None:
    utc_timestamp = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()

    if monthlyTimer.past_due:
        logging.info("The timer is past due!")

    prs = load_jsonl_string_into_df(prsIn)
    projects = load_jsonl_string_into_df(projectsIn)
    contributors = load_jsonl_string_into_df(contributorsIn)

    table_image_bytes = create_monthly_table(prs, projects, contributors)
    tableOut.set(table_image_bytes)

    logging.info("Python timer trigger function ran at %s", utc_timestamp)
