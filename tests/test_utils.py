from datetime import date

from utils.filter import filter_nr_stars, filter_on_recency


def test_filter_on_recensy(analysis_table):
    start_date = date(year=2022, month=10, day=1)
    end_date = date.today()
    filtered_table = filter_on_recency(analysis_table, start_date, end_date)
    assert len(filtered_table) == 2


def test_filter_pull_requests_start_date(analysis_table):
    prs_including = filter_on_recency(
        analysis_table, date(year=2022, month=11, day=22), date.today()
    )
    prs_excluding = filter_on_recency(
        analysis_table, date(year=2022, month=11, day=23), date.today()
    )
    assert len(prs_including) == 1 and prs_excluding.empty


def test_filter_pull_requests_end_date(analysis_table):
    prs_including = filter_on_recency(
        analysis_table,
        date(year=2020, month=1, day=1),
        date(year=2022, month=11, day=23),
    )
    prs_excluding = filter_on_recency(
        analysis_table,
        date(year=2020, month=1, day=1),
        date(year=2022, month=11, day=22),
    )
    assert len(prs_including) == 4 and len(prs_excluding) == 3


def test_filter_pull_requests_stars(analysis_table):
    prs_including = filter_nr_stars(analysis_table, minimum_stars=20)
    prs_excluding = filter_nr_stars(analysis_table, minimum_stars=21)
    assert len(prs_including) == 1 and prs_excluding.empty
