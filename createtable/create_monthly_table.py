import io
import os
from datetime import date
from typing import Tuple

import dataframe_image as dfi
import pandas as pd
from dateutil.relativedelta import relativedelta

from utils.filter import create_analysis_table


class EmptyDataFrameError(Exception):
    pass


def create_monthly_table(
    pull_requests: pd.DataFrame, projects: pd.DataFrame, contributors: pd.DataFrame
) -> bytes:
    start_day, end_day = get_last_month_date_range()

    last_months_pull_requests = create_analysis_table(
        pull_requests,
        projects,
        contributors,
        minimum_stars=int(os.environ.get("MINIMUM_STARS")),
        start_date=start_day,
        end_date=end_day,
    )

    return create_table_image_bytes(last_months_pull_requests)


def get_last_month_date_range() -> Tuple[date, date]:
    """
    Get the first and last days of last month.
    """
    today = date.today()
    first_day_this_month = date(year=today.year, month=today.month, day=1)
    first_day_last_month = first_day_this_month - relativedelta(months=1)
    return first_day_last_month, first_day_this_month


def create_table_image_bytes(pull_requests: pd.DataFrame) -> bytes:
    """
    Convert the pull requests into image bytes of the corresponding table.
    """
    if pull_requests.empty:
        raise EmptyDataFrameError("PR DataFrame is empty")

    monthly_table = format_table(pull_requests)
    image_bytes = export_df_to_image_bytes(monthly_table)
    return image_bytes


def format_table(pull_requests: pd.DataFrame) -> pd.DataFrame:
    """
    Apply changes to the table for aesthetics.
    """
    table = (
        pull_requests.pipe(select_table_columns)
        .pipe(rename_columns)
        .assign(Date=lambda row: pd.to_datetime(row["Date"]).dt.date)
        .sort_values(by="Date")
        .reset_index(drop=True)
    )

    return table


def select_table_columns(pull_requests: pd.DataFrame) -> pd.DataFrame:
    return pull_requests[["project_name", "contributor_name", "closed_at", "pr_title"]]


def rename_columns(pull_requests: pd.DataFrame) -> pd.DataFrame:
    return pull_requests.rename(
        columns={
            "project_name": "Project",
            "contributor_name": "Contributor",
            "closed_at": "Date",
            "pr_title": "PR Title",
        }
    )


def export_df_to_image_bytes(df: pd.DataFrame) -> bytes:
    """
    Convert the DataFrame to a buffer containing the image bytes.
    """
    pd.set_option("colheader_justify", "left")
    pd.set_option("display.max_colwidth", None)

    buffer = io.BytesIO()
    dfi.export(
        df,
        buffer,
        table_conversion="matplotlib",
        dpi=300,
    )
    return buffer.getvalue()
