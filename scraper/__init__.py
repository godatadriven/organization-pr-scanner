import datetime
import logging
from typing import Dict, List

import azure.functions as func

from scraper.scraper import build_string_output, scraper
from utils.filter import string_to_jsonl


def update_storage(
    prs: List[Dict],
    projects: List[Dict],
    contributors: List[Dict],
    prsOut: func.Out[str],
    projectsOut: func.Out[str],
    contributorsOut: func.Out[str],
):
    """
    Set the jsonl files in blob storage with the updated data.
    """
    prs_output = build_string_output(prs)
    projects_output = build_string_output(projects)
    contributors_output = build_string_output(contributors)

    prsOut.set(prs_output)
    projectsOut.set(projects_output)
    contributorsOut.set(contributors_output)


def main(
    scraperTimer: func.TimerRequest,
    prsIn: str,
    projectsIn: str,
    contributorsIn: str,
    prsOut: func.Out[str],
    projectsOut: func.Out[str],
    contributorsOut: func.Out[str],
) -> None:
    utc_timestamp = (
        datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    )

    if scraperTimer.past_due:
        logging.info("The timer is past due!")

    pull_requests = string_to_jsonl(prsIn)
    projects = string_to_jsonl(projectsIn)
    contributors = string_to_jsonl(contributorsIn)

    updated_pull_requests, updated_projects, updated_contributors = scraper(
        pull_requests, projects, contributors
    )

    # Only update if there are new pull requests
    if len(updated_pull_requests) > len(pull_requests):
        update_storage(
            updated_pull_requests,
            updated_projects,
            updated_contributors,
            prsOut,
            projectsOut,
            contributorsOut,
        )

    logging.info("Python timer trigger function ran at %s", utc_timestamp)
