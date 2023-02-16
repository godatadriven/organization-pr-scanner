from calendar import monthrange
from datetime import datetime

from dateutil.relativedelta import relativedelta

from createtable.create_monthly_table import get_last_month_date_range


def test_get_last_month_date_range_days():
    first_day, last_day = get_last_month_date_range()
    last_month_dt = datetime.today() - relativedelta(months=1)
    nr_days_in_month = monthrange(year=last_month_dt.year, month=last_month_dt.month)[1]
    assert (last_day - first_day).days == nr_days_in_month
