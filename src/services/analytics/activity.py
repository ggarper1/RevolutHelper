from dataclasses import dataclass
from datetime import datetime
import pandas as pd
from typing import List

from src.storage.transaction_database import Transaction_Database
from src.storage.models.transaction import Transaction

from src.entities.time_granularity import Time_Granularity
from src.entities.result import Result

from src.services.analytics.utils import ceil_date, floor_date, get_transactions_between


@dataclass
class Grouped_Income_Outcome:
    start_date: datetime
    positive_sum: float
    negative_sum: float
    balance: float


def get_grouped_incomes_outcomes(
    db: Transaction_Database,
    start_date: datetime,
    end_date: datetime,
    granularity: Time_Granularity,
) -> Result[List[Grouped_Income_Outcome]]:
    start_date = floor_date(start_date, granularity)
    end_date = ceil_date(end_date, granularity)

    result = get_transactions_between(db, start_date, end_date)
    if not result.ok:
        return Result.failure(result.error or "")

    assert result.data is not None
    filtered = result.data

    grouped = (
        filtered.assign(
            pos_vals=filtered[Transaction.AMOUNT].clip(lower=0),
            neg_vals=filtered[Transaction.AMOUNT].clip(upper=0),
        )
        .groupby(pd.Grouper(key=Transaction.START_DATE, freq=granularity.value))
        .agg(
            positive_sum=("pos_vals", "sum"),
            negative_sum=("neg_vals", "sum"),
            period_balance=(Transaction.BALANCE, "last"),
        )
        .dropna()
        .reset_index()
    ).rename(columns={Transaction.START_DATE: "start_date"})

    return Result.success(
        [
            Grouped_Income_Outcome(
                start_date=row.start_date.to_pydatetime(),  # type: ignore
                positive_sum=row.positive_sum,  # type: ignore
                negative_sum=row.negative_sum,  # type: ignore
                balance=row.period_balance,  # type: ignore
            )
            for row in grouped.itertuples(index=False)
        ]
    )
