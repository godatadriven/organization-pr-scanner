import pathlib

import pytest

from utils.filter import (
    load_jsonl_df_from_path,
    load_jsonl_from_path,
    merge_projects_and_contributors,
)


@pytest.fixture
def pull_requests():
    return load_jsonl_df_from_path(
        pathlib.Path(__file__).parent / "test_data" / "test_pullrequests.jsonl"
    )


@pytest.fixture
def projects():
    return load_jsonl_df_from_path(
        pathlib.Path(__file__).parent / "test_data" / "test_projects.jsonl"
    )


@pytest.fixture
def contributors():
    return load_jsonl_df_from_path(
        pathlib.Path(__file__).parent / "test_data" / "test_contributors.jsonl"
    )


@pytest.fixture
def pull_requests_jsonl():
    return load_jsonl_from_path(
        pathlib.Path(__file__).parent / "test_data" / "test_pullrequests.jsonl"
    )


@pytest.fixture
def pull_requests_jsonl_duplicate():
    return load_jsonl_from_path(
        pathlib.Path(__file__).parent
        / "test_data"
        / "test_pullrequests_duplicate.jsonl"
    )


@pytest.fixture
def analysis_table(pull_requests, projects, contributors):
    return merge_projects_and_contributors(pull_requests, projects, contributors)
