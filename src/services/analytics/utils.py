from datetime import datetime, timedelta
from calendar import monthrange

from pandas import DataFrame

from src.entities.time_granularity import Time_Granularity
from src.storage.transaction_database import Transaction_Database
from src.storage.models.transaction import Transaction

from src.entities.result import Result


def floor_date(date_time: datetime, granularity: Time_Granularity):
    date_time = date_time.replace(hour=0, minute=0, second=0)

    if granularity == Time_Granularity.WEEK:
        date_time -= timedelta(days=date_time.weekday())
    elif granularity == Time_Granularity.MONTH:
        date_time = date_time.replace(day=1)
    elif granularity == Time_Granularity.YEAR:
        date_time = date_time.replace(month=1, day=1)

    return date_time


def ceil_date(date_time: datetime, granularity: Time_Granularity):
    date_time = date_time.replace(hour=23, minute=59, second=59)

    if granularity == Time_Granularity.WEEK:
        date_time += timedelta(days=6 - date_time.weekday())
    elif granularity == Time_Granularity.MONTH:
        last_day = monthrange(date_time.year, date_time.month)[1]
        date_time = date_time.replace(day=last_day)
    elif granularity == Time_Granularity.YEAR:
        date_time = date_time.replace(month=12, day=31)

    return date_time


def get_transactions_between(
    db: Transaction_Database,
    start_date: datetime,
    end_date: datetime,
) -> Result[DataFrame]:
    if start_date > end_date:
        return Result.failure("start_date > end_date")

    mask = db.dt[Transaction.START_DATE].between(start_date, end_date)

    return Result.success(db.dt[mask])
