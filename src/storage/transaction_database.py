from datetime import datetime
from enum import Enum
from os.path import isfile
from typing import Tuple, Optional, cast
import pandas as pd


class Transaction(str, Enum):
    TYPE = "Type"
    PRODUCT = "Product"
    START_DATE = "Started Date"
    COMPLETED_DATE = "Completed Date"
    DESCRIPTION = "Description"
    AMOUNT = "Amount"
    FEE = "Fee"
    CURRENCY = "Currency"
    STATE = "State"
    BALANCE = "Balance"

    @classmethod
    def columns(cls):
        return [
            cls.TYPE,
            cls.PRODUCT,
            cls.START_DATE,
            cls.COMPLETED_DATE,
            cls.DESCRIPTION,
            cls.AMOUNT,
            cls.FEE,
            cls.CURRENCY,
            cls.STATE,
            cls.BALANCE,
        ]


DATA_FILE_NAME = "./data/global.csv"

DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class Transaction_Database:
    def __init__(self, db_file_name: str = DATA_FILE_NAME):
        self.db_file_name = db_file_name

        if not isfile(db_file_name):
            columns = Transaction.columns()
            self.dt: pd.DataFrame = pd.DataFrame(columns=pd.Index(columns))

            self.dt.to_csv(db_file_name, index=False)
        else:
            self.dt: pd.DataFrame = pd.read_csv(
                db_file_name,
                parse_dates=[Transaction.START_DATE, Transaction.COMPLETED_DATE],
                date_format="%Y-%m-%d %H:%M:%S",
            )

    def add_transactions(self, file) -> Tuple[int, Optional[Tuple[datetime, datetime]]]:
        new_data = pd.read_csv(
            file,
            parse_dates=[Transaction.START_DATE, Transaction.COMPLETED_DATE],
            date_format="%Y-%m-%d %H:%M:%S",
        )

        if len(new_data) == 0:
            return 0, None

        if len(self.dt) == 0:
            self.dt = new_data
            self.dt.to_csv(self.db_file_name, index=False)
            return len(new_data), None

        oldest_new_date = cast(datetime, new_data[Transaction.START_DATE].iloc[0])
        latest_new_date = cast(datetime, new_data[Transaction.START_DATE].iloc[-1])

        oldest_registered_date = cast(
            datetime, pd.Series(self.dt[Transaction.START_DATE]).iloc[0]
        )
        latest_registered_date = cast(
            datetime, pd.Series(self.dt[Transaction.START_DATE]).iloc[-1]
        )

        if (
            latest_new_date < latest_registered_date
            and oldest_new_date > oldest_registered_date
        ):
            return 0, None

        num_transactions_added, gap = 0, None
        if oldest_new_date < oldest_registered_date:
            mask = new_data[Transaction.START_DATE] < oldest_registered_date
            to_append = new_data[mask]

            if latest_new_date < oldest_registered_date:
                max_mask_date = to_append[Transaction.START_DATE].max()
                gap = (
                    cast(datetime, max_mask_date),
                    oldest_registered_date,
                )

            self.dt = pd.DataFrame(pd.concat([to_append, self.dt], ignore_index=True))
            num_transactions_added += len(to_append)

        if latest_new_date > latest_registered_date:
            mask = new_data[Transaction.START_DATE] > latest_registered_date
            to_append = new_data[mask]

            if oldest_new_date > latest_registered_date:
                min_mask_date = to_append[Transaction.START_DATE].min()
                gap = (
                    latest_registered_date,
                    cast(datetime, min_mask_date),
                )

            self.dt = pd.DataFrame(pd.concat([self.dt, to_append], ignore_index=True))
            num_transactions_added += len(to_append)

        self.dt.to_csv(self.db_file_name, index=False)

        return num_transactions_added, gap
