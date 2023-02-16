import json
import logging
import os
import time
from collections.abc import Generator
from datetime import date, datetime
from operator import attrgetter
from typing import Any, Dict, List, Tuple

from dateutil.relativedelta import relativedelta
from github import Github, RateLimitExceededException
from github.NamedUser import NamedUser
from tqdm import tqdm

from definitions import CONTRIBUTOR_FIELDS, PR_FIELDS, PROJECT_FIELDS


def write_json_line(json_lines: List[Dict], line: Dict) -> None:
    json_lines.append(line)


def build_string_output(json_lines: List[Dict]) -> str:
    output = ""
    for line in json_lines:
        output += json.dumps(line, default=str) + "\n"
    return output


def sleep_until_reset(reset_time: int) -> None:
    sleep_time = reset_time - int(time.time()) + 10
    time.sleep(sleep_time)


def extract_relevant_fields(data: Any, field_map: Dict[str, str]) -> Dict:
    """
    Extract a set of key-value pairs from an object, change their key according to map,
    and return them in a dictionary format.
    """
    field_getter = attrgetter(*field_map.keys())
    fields = field_getter(data)
    new_keys = field_map.values()
    return dict(zip(new_keys, fields))


def get_new_pull_requests_and_projects(
    github: Github, pr_iterator: Generator
) -> Tuple[List[Dict], List[Dict]]:
    """
    Extract pull requests and unique corresponding projects from a generator.
    """
    projects = []
    project_ids = []
    pull_requests = []

    while True:
        try:
            pr = next(pr_iterator)
            assert not pr.repository.private
            write_json_line(pull_requests, extract_relevant_fields(pr, PR_FIELDS))
            if pr.repository.id not in project_ids:
                write_json_line(
                    projects,
                    extract_relevant_fields(pr.repository, PROJECT_FIELDS),
                )
                project_ids.append(pr.repository.id)

        except StopIteration:
            return pull_requests, projects

        # sleep until rate renewal if the rate limit is reached
        except RateLimitExceededException:
            rate_reset_timestamp = github.rate_limiting_resettime
            reset_time = datetime.fromtimestamp(rate_reset_timestamp).time()
            logging.info(f"Rate Limit Exceeded, waiting till {reset_time}")
            sleep_until_reset(rate_reset_timestamp)
            continue


def scrape_pull_requests_for_user(
    github: Github, user: NamedUser, start_date: date, end_date: date
) -> Tuple[List[Dict], List[Dict]]:
    """
    Scrape all pull requests and project for a given user over a specified period.
    """
    logging.info(f"Processing {user.login}")

    # query merged, public pull requests between the two dates
    query = (
        f"author:{user.login} is:pull-request "
        f"type:pr is:public "
        f"merged:{start_date.strftime('%Y-%m-%d')}..{end_date.strftime('%Y-%m-%d')}"
    )
    closed_prs_iter = iter(github.search_issues(query=query))

    pull_requests, projects = get_new_pull_requests_and_projects(
        github, closed_prs_iter
    )

    return pull_requests, projects


def scrape_organization_data(
    organization: str, start_date: date, end_date: date
) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """
    Scrape pull requests, projects and contributors for a given organization,
    between two dates
    """
    pull_requests, projects, contributors = [], [], []

    github = Github(os.environ.get("GITHUB_TOKEN"))
    organization = github.get_organization(organization)

    for user in tqdm(organization.get_members()):
        write_json_line(contributors, extract_relevant_fields(user, CONTRIBUTOR_FIELDS))
        user_pull_requests, user_projects = scrape_pull_requests_for_user(
            github, user, start_date, end_date
        )
        pull_requests += user_pull_requests
        projects += user_projects

    return pull_requests, projects, contributors


def update_jsonl_on_unique_key(
    originals: List[Dict], candidates: List[Dict], key: str
) -> List[Dict]:
    """
    Extend a list of dictionaries with a set of candidates if they are not already
    in the original.
    """
    keys = {line[key] for line in originals}
    distinct_candidates = [line for line in candidates if line[key] not in keys]
    return originals + distinct_candidates


def integrate_new_data(
    pull_requests: List[Dict],
    projects: List[Dict],
    contributors: List[Dict],
    new_pull_requests: List[Dict],
    new_projects: List[Dict],
    new_contributors: List[Dict],
):
    updated_pull_requests = update_jsonl_on_unique_key(
        pull_requests,
        new_pull_requests,
        "pr_id",
    )
    updated_projects = update_jsonl_on_unique_key(
        projects,
        new_projects,
        "project_id",
    )
    updated_contributors = update_jsonl_on_unique_key(
        contributors,
        new_contributors,
        "contributor_login",
    )
    return updated_pull_requests, updated_projects, updated_contributors


def scraper(
    pull_requests: List[Dict], projects: List[Dict], contributors: List[Dict]
) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """
    Update the pull_requests, projects and contributors with newly scraped data
    up until today.
    """

    yesterday = date.today() - relativedelta(days=1)
    month_ago = date.today() - relativedelta(months=1)

    new_pull_requests, new_projects, new_contributors = scrape_organization_data(
        organization=os.environ.get("ORGANIZATION"),
        start_date=month_ago,
        end_date=yesterday,
    )

    updated_pull_requests, updated_projects, updated_contributors = integrate_new_data(
        pull_requests,
        projects,
        contributors,
        new_pull_requests,
        new_projects,
        new_contributors,
    )

    return updated_pull_requests, updated_projects, updated_contributors
