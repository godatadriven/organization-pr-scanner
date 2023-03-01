import logging
from datetime import datetime, timezone

import azure.functions as func

from sendtable.monthly_pr_table import image_bytes_to_buffer, send_monthly_pr_table


def main(monthlyTimer: func.TimerRequest, tableIn: bytes) -> None:
    utc_timestamp = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()

    if monthlyTimer.past_due:
        logging.info("The timer is past due!")

    table_buffer = image_bytes_to_buffer(tableIn)
    send_monthly_pr_table(table_buffer)
    logging.info("Python timer trigger function ran at %s", utc_timestamp)
