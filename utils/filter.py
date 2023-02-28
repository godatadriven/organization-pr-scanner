import json
import os
import pathlib
from datetime import date
from typing import Dict, List

import pandas as pd


def load_jsonl_df_from_path(jsonl_path: pathlib.Path) -> pd.DataFrame:
    return load_jsonl_string_into_df(jsonl_path.read_text())


def load_jsonl_from_path(jsonl_path: pathlib.Path) -> List[Dict]:
    return string_to_jsonl(jsonl_path.read_text())


def load_jsonl_string_into_df(jsonl_string: str) -> pd.DataFrame():
    json_lines = [json.loads(line) for line in jsonl_string.splitlines()]
    return pd.DataFrame(json_lines)


def string_to_jsonl(string: str) -> List[Dict]:
    return [json.loads(line) for line in string.splitlines()]


def filter_on_recency(
    prs: pd.DataFrame, start_date: date, end_date: date
) -> pd.DataFrame:
    closed_dates = pd.to_datetime(prs["closed_at"]).dt.date
    prs = prs.loc[(closed_dates >= start_date) & (closed_dates < end_date)]
    return prs


def filter_nr_stars(prs: pd.DataFrame, minimum_stars: int) -> pd.DataFrame:
    prs = prs.loc[lambda df: df["stars"] >= minimum_stars]
    return prs


def remove_self_owned(prs: pd.DataFrame, exclude_own_projects: bool) -> pd.DataFrame:
    if exclude_own_projects:
        return prs.loc[lambda df: df["contributor_login"] != df["owner_login"]]
    return prs


def remove_org_owned(prs: pd.DataFrame, exclude_org_projects: bool) -> pd.DataFrame:
    if exclude_org_projects:
        return prs.loc[lambda df: df["owner_login"] != os.environ.get("ORGANIZATION")]
    return prs


def fill_missing_names_with_logins(prs: pd.DataFrame) -> pd.DataFrame:
    return prs.assign(
        contributor_name=prs["contributor_name"].fillna(value=prs["contributor_login"])
    )


def merge_projects_and_contributors(
    pull_requests: pd.DataFrame, projects: pd.DataFrame, contributors: pd.DataFrame
) -> pd.DataFrame:
    return pull_requests.merge(
        projects,
        how="left",
        left_on="repository_id",
        right_on="project_id",
    ).merge(
        contributors,
        how="left",
        left_on="contributor_login",
        right_on="contributor_login",
    )


def create_analysis_table(
    pull_requests: pd.DataFrame,
    projects: pd.DataFrame,
    contributors: pd.DataFrame,
    minimum_stars: int,
    start_date: date,
    end_date: date,
) -> pd.DataFrame:
    """
    Merge pull requests, projects and contributors and apply filters according to
    the given stars and date parameters
    """
    pull_requests = (
        merge_projects_and_contributors(pull_requests, projects, contributors)
        .pipe(filter_on_recency, start_date, end_date)
        .pipe(filter_nr_stars, minimum_stars)
        .pipe(fill_missing_names_with_logins)
    )

    return pull_requests.reset_index(drop=True)
