from datetime import datetime, timedelta
import pandas as pd

from src.storage.models.transaction import Transaction
from src.entities.time_granularity import Time_Granularity
from src.storage.transaction_database import Transaction_Database
from src.services.analytics.activity import get_grouped_incomes_outcomes


class Test_Get_Grouped_Incomes_Outcomes:
    TEST_DATA = "./tests/data/src/services/analytics/activity_test_data.csv"

    def test_errors(self):
        db = Transaction_Database(
            db_file_name=Test_Get_Grouped_Incomes_Outcomes.TEST_DATA
        )

        start_date = datetime(year=2025, month=5, day=4, hour=12, minute=34, second=45)
        result = get_grouped_incomes_outcomes(
            db, start_date, start_date - timedelta(days=3), Time_Granularity.DAY
        )

        assert not result.ok

    def test_all_cases(self):
        db = Transaction_Database(
            db_file_name=Test_Get_Grouped_Incomes_Outcomes.TEST_DATA
        )

        def helper(
            db: Transaction_Database,
            granularity: Time_Granularity,
            start_date: datetime,
            end_date: datetime,
            expected_result: list,
        ):
            result = get_grouped_incomes_outcomes(db, start_date, end_date, granularity)
            s = f"""Granularity: {granularity}
                    start_date: {start_date}
                    end_date: {end_date}
                """
            assert result.ok and result.data is not None, s
            print("\n".join(str(d) for d in result.data))
            print("\n\n")

            assert len(result.data) == len(expected_result), s

            for row, expected in zip(result.data, expected_result):
                (
                    expected_start_date,
                    expected_positive,
                    expected_negative,
                    expected_balance,
                ) = expected

                assert row.start_date == expected_start_date
                assert row.positive_sum == expected_positive
                assert row.negative_sum == expected_negative
                assert row.balance == expected_balance

        # Day granularity:
        day_data = [
            (
                datetime(year=2026, month=3, day=2, hour=12, minute=4, second=40),
                datetime(year=2026, month=3, day=2, hour=12, minute=54, second=56),
                [
                    (datetime(year=2026, month=3, day=2), 0.0, -1050.0, 1950.0),
                ],
            ),
            (
                datetime(year=2026, month=3, day=1, hour=11, minute=50, second=4),
                datetime(year=2026, month=3, day=15, hour=9, minute=59, second=1),
                [
                    (datetime(year=2026, month=3, day=1), 3000.0, 0.0, 3000.0),
                    (datetime(year=2026, month=3, day=2), 0.0, -1050.0, 1950.0),
                    (datetime(year=2026, month=3, day=15), 200.0, 0.0, 2150.0),
                ],
            ),
            (
                datetime(year=2026, month=3, day=15, hour=4, minute=23, second=4),
                datetime(year=2026, month=4, day=1, hour=0, minute=9, second=9),
                [
                    (datetime(year=2026, month=3, day=15), 200.0, 0.0, 2150.0),
                    (datetime(year=2026, month=4, day=1), 0.0, -500.0, 1650.0),
                ],
            ),
            (
                datetime(year=2026, month=3, day=10, hour=10, minute=40, second=50),
                datetime(year=2026, month=3, day=15, hour=20, minute=20, second=20),
                [
                    (datetime(year=2026, month=3, day=15), 200.0, 0.0, 2150.0),
                ],
            ),
        ]

        for start_date, end_date, data in day_data:
            helper(db, Time_Granularity.DAY, start_date, end_date, data)

        # Week granularity:
        week_data = [
            (
                datetime(year=2026, month=3, day=2, hour=12, minute=10, second=5),
                datetime(year=2026, month=3, day=2, hour=14, minute=45, second=6),
                [
                    (datetime(year=2026, month=3, day=8), 0.0, -1050.0, 1950.0),
                ],
            ),
            (
                datetime(year=2026, month=3, day=1, hour=12, minute=54, second=3),
                datetime(year=2026, month=3, day=8, hour=4, minute=5, second=54),
                [
                    (datetime(year=2026, month=3, day=1), 3000.0, 0.0, 3000.0),
                    (datetime(year=2026, month=3, day=8), 0.0, -1050.0, 1950.0),
                ],
            ),
            (
                datetime(year=2026, month=3, day=1, hour=7, minute=33, second=12),
                datetime(year=2026, month=3, day=15, hour=16, minute=44, second=8),
                [
                    (datetime(year=2026, month=3, day=1), 3000.0, 0.0, 3000.0),
                    (datetime(year=2026, month=3, day=8), 0.0, -1050.0, 1950.0),
                    (datetime(year=2026, month=3, day=15), 200.0, 0.0, 2150.0),
                ],
            ),
            (
                datetime(year=2026, month=3, day=15, hour=9, minute=17, second=52),
                datetime(year=2026, month=4, day=1, hour=11, minute=3, second=27),
                [
                    (datetime(year=2026, month=3, day=15), 200.0, 0.0, 2150.0),
                    (datetime(year=2026, month=4, day=5), 0.0, -500.0, 1650.0),
                ],
            ),
        ]

        for start_date, end_date, data in week_data:
            helper(db, Time_Granularity.WEEK, start_date, end_date, data)

        # Month granularity:
        month_data = [
            (
                datetime(year=2026, month=3, day=2, hour=12, minute=0, second=0),
                datetime(year=2026, month=3, day=2, hour=12, minute=0, second=0),
                [
                    (datetime(year=2026, month=3, day=31), 3200.0, -1050.0, 2150.0),
                ],
            ),
            (
                datetime(year=2026, month=3, day=1, hour=8, minute=22, second=11),
                datetime(year=2026, month=4, day=1, hour=14, minute=37, second=59),
                [
                    (datetime(year=2026, month=3, day=31), 3200.0, -1050.0, 2150.0),
                    (datetime(year=2026, month=4, day=30), 0.0, -500.0, 1650.0),
                ],
            ),
            (
                datetime(year=2026, month=4, day=1, hour=3, minute=15, second=44),
                datetime(year=2026, month=4, day=30, hour=18, minute=52, second=7),
                [
                    (datetime(year=2026, month=4, day=30), 0.0, -500.0, 1650.0),
                ],
            ),
            (
                datetime(year=2025, month=12, day=21, hour=16, minute=5, second=30),
                datetime(year=2026, month=3, day=15, hour=11, minute=48, second=19),
                [
                    (datetime(year=2025, month=12, day=31), 0.0, -10.0, 0.0),
                    (datetime(year=2026, month=3, day=31), 3200.0, -1050.0, 2150.0),
                ],
            ),
        ]

        for start_date, end_date, data in month_data:
            helper(db, Time_Granularity.MONTH, start_date, end_date, data)

        # Year granularity:
        year_data = [
            (
                datetime(year=2026, month=3, day=2, hour=12, minute=0, second=0),
                datetime(year=2026, month=3, day=2, hour=12, minute=0, second=0),
                [
                    (datetime(year=2026, month=12, day=31), 3200.0, -1550.0, 1650.0),
                ],
            ),
            (
                datetime(year=2025, month=12, day=21, hour=19, minute=41, second=3),
                datetime(year=2026, month=4, day=1, hour=7, minute=29, second=55),
                [
                    (datetime(year=2025, month=12, day=31), 0.0, -10.0, 0.0),
                    (datetime(year=2026, month=12, day=31), 3200.0, -1550.0, 1650.0),
                ],
            ),
            (
                datetime(year=2026, month=1, day=1, hour=5, minute=58, second=17),
                datetime(year=2026, month=6, day=30, hour=22, minute=14, second=36),
                [
                    (datetime(year=2026, month=12, day=31), 3200.0, -1550.0, 1650.0),
                ],
            ),
            (
                datetime(year=2025, month=12, day=1, hour=13, minute=7, second=28),
                datetime(year=2025, month=12, day=31, hour=20, minute=33, second=51),
                [
                    (datetime(year=2025, month=12, day=31), 0.0, -10.0, 0.0),
                ],
            ),
        ]

        for start_date, end_date, data in year_data:
            helper(db, Time_Granularity.YEAR, start_date, end_date, data)

    def test_no_data(self):
        db = Transaction_Database(
            db_file_name=Test_Get_Grouped_Incomes_Outcomes.TEST_DATA
        )

        db.dt = pd.DataFrame(columns=Transaction.columns())

        now = datetime.now()
        result = get_grouped_incomes_outcomes(
            db, now - timedelta(days=30), now, Time_Granularity.DAY
        )
        assert result.ok
        assert result.data is not None and len(result.data) == 0
