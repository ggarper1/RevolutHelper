from datetime import datetime
import pytest
from os import remove
from os.path import exists
import pandas as pd

from src.storage.transaction_database import (
    Transaction_Database,
    Transaction,
    DATE_TIME_FORMAT,
)


class Test_Transaction_Database:
    TEMP = "./tests/data/src/transaction_database/temp.csv"

    @pytest.fixture(autouse=True)
    def clean_up(self):
        yield

        clean_ups = [Test_Transaction_Database.TEMP]

        for to_clean_up in clean_ups:
            if exists(Test_Transaction_Database.TEMP):
                remove(to_clean_up)

    def test_case_all_cases_add_transactions(self):
        # =============================================================================
        # TEST DATA FOR CSV TRANSACTION IMPORT SCENARIOS
        # =============================================================================
        #
        # Legend:  [====]  registered (base) range
        #          [----]  case-specific range
        #          [####]  overlap between the two
        #
        # All diagrams share the same timeline ruler:
        #
        #   Jan 05   Jan 25   Feb 03             Feb 20   Feb 22   Mar 07
        #   |        |        |                  |        |        |
        #   ·········|········|··················|········|········|·······>
        #
        # =============================================================================

        # -----------------------------------------------------------------------------
        # BASE  (registered_csv_data)                          Feb 03 ──── Feb 20
        # -----------------------------------------------------------------------------
        #
        #   Jan 05   Jan 25   Feb 03             Feb 20   Feb 22   Mar 07
        #   |        |        |                  |        |        |
        #            ·········[==================]·····················>
        #                      registered
        #
        # -----------------------------------------------------------------------------
        REGISTERED_CSV_PATH = "./tests/data/src/transaction_database/registered.csv"

        # -----------------------------------------------------------------------------
        # CASE A — All transactions OLDER than base        Jan 05 ──── Jan 31
        # -----------------------------------------------------------------------------
        #
        #   Jan 05   Jan 25   Feb 03             Feb 20   Feb 22   Mar 07
        #   |        |        |                  |        |        |
        #   [--------]·······[==================]·····················>
        #    case_a   · gap ·  registered
        #
        # -----------------------------------------------------------------------------
        CASE_A_CSV_PATH = "./tests/data/src/transaction_database/case_a.csv"

        # -----------------------------------------------------------------------------
        # CASE B — Starts before base, ends before base ends  Jan 28 ──── Feb 19
        # -----------------------------------------------------------------------------
        #
        #   Jan 05   Jan 25   Feb 03             Feb 20   Feb 22   Mar 07
        #   |        |        |                  |        |        |
        #            ·········[==================]·····················>
        #            [--------[#########]·········
        #             case_b  ^ overlap   case_b ends before registered
        #
        # -----------------------------------------------------------------------------
        CASE_B_CSV_PATH = "./tests/data/src/transaction_database/case_b.csv"

        # -----------------------------------------------------------------------------
        # CASE C — Subset: fewer rows, all within base range   Feb 07 ──── Feb 17
        # -----------------------------------------------------------------------------
        #
        #   Jan 05   Jan 25   Feb 03             Feb 20   Feb 22   Mar 07
        #   |        |        |                  |        |        |
        #            ·········[==================]·····················>
        #                          [######]
        #                           case_c (4 rows taken from registered)
        #
        # -----------------------------------------------------------------------------
        CASE_C_CSV_PATH = "./tests/data/src/transaction_database/case_c.csv"

        # -----------------------------------------------------------------------------
        # CASE D — Starts within base, ends after base ends    Feb 03 ──── Feb 28
        # -----------------------------------------------------------------------------
        #
        #   Jan 05   Jan 25   Feb 03             Feb 20   Feb 22   Mar 07
        #   |        |        |                  |        |        |
        #            ·········[==================]·····················>
        #                     [#################]--------]
        #                      overlap            case_d only
        #
        # -----------------------------------------------------------------------------
        CASE_D_CSV_PATH = "./tests/data/src/transaction_database/case_d.csv"

        # -----------------------------------------------------------------------------
        # CASE E — All transactions NEWER than base            Feb 22 ──── Mar 07
        # -----------------------------------------------------------------------------
        #
        #   Jan 05   Jan 25   Feb 03             Feb 20   Feb 22   Mar 07
        #   |        |        |                  |        |        |
        #            ·········[==================]·····················>
        #                                          · gap ·[--------]
        #                                                  case_e
        #
        # -----------------------------------------------------------------------------
        CASE_E_CSV_PATH = "./tests/data/src/transaction_database/case_e.csv"

        # -----------------------------------------------------------------------------
        # CASE F — Base is a strict subset of case_f          Jan 25 ──── Feb 28
        # -----------------------------------------------------------------------------
        #
        #   Jan 05   Jan 25   Feb 03             Feb 20   Feb 22   Mar 07
        #   |        |        |                  |        |        |
        #            ·········[==================]·····················>
        #            [--------[##################]--------]
        #             case_f    overlap (all of registered)  case_f
        #
        # -----------------------------------------------------------------------------
        CASE_F_CSV_PATH = "./tests/data/src/transaction_database/case_f.csv"

        def string_diff(case, registered_dt, combined_dt):
            s = f"\n{case}\nExpected length: {len(combined_dt)}, got: {len(registered_dt)}\n"
            idx = 0
            while idx < min(len(registered_dt), len(combined_dt)):
                s += f"{registered_dt[Transaction.START_DATE][idx]}, {registered_dt[Transaction.BALANCE][idx]:>5.2f}\t"
                s += f"{combined_dt[Transaction.START_DATE][idx]}, {combined_dt[Transaction.BALANCE][idx]:>5.2f}\n"
                idx += 1

            while idx < len(registered_dt):
                s += f"{registered_dt[Transaction.START_DATE][idx]}, {registered_dt[Transaction.BALANCE][idx]:>5.2f}\n"
                idx += 1

            while idx < len(combined_dt):
                padding = " " * 30
                s += f"{padding}{combined_dt[Transaction.START_DATE][idx]}, {combined_dt[Transaction.BALANCE][idx]:>5.2f}\n"
                idx += 1

            s += "\n"

            for col in Transaction.columns():
                idx = 0
                while idx < min(len(registered_dt), len(combined_dt)):
                    s += f"{type(registered_dt[col][idx])}\t{type(combined_dt[col][idx])}\n"
                    idx += 1
                while idx < len(registered_dt):
                    s += f"{type(registered_dt[col][idx])}\n"
                    idx += 1
                while idx < len(combined_dt):
                    s += f"{' ' * 22}\t{type(combined_dt[col][idx])}\n"
                    idx += 1
                s += "\n"

            return s

        def assert_all_transactions_added(
            db: Transaction_Database, registered_file_path, added_file_path
        ):
            registered_dt = pd.read_csv(
                registered_file_path,
                parse_dates=[Transaction.START_DATE, Transaction.COMPLETED_DATE],
                date_format="%Y-%m-%d %H:%M:%S",
            )
            added_dt = pd.read_csv(
                added_file_path,
                parse_dates=[Transaction.START_DATE, Transaction.COMPLETED_DATE],
                date_format="%Y-%m-%d %H:%M:%S",
            )
            combined = pd.concat(
                [registered_dt, added_dt],
                ignore_index=True,
            ).drop_duplicates()

            sorted_combined = combined.sort_values(
                Transaction.START_DATE, ascending=True
            ).reset_index(drop=True)

            assert db.dt.equals(sorted_combined), string_diff(
                added_file_path, db.dt, sorted_combined
            )
            assert pd.read_csv(
                Test_Transaction_Database.TEMP,
                parse_dates=[Transaction.START_DATE, Transaction.COMPLETED_DATE],
                date_format="%Y-%m-%d %H:%M:%S",
            ).equals(sorted_combined), string_diff(
                added_file_path, db.dt, sorted_combined
            )

        cases = [
            CASE_A_CSV_PATH,
            CASE_B_CSV_PATH,
            CASE_C_CSV_PATH,
            CASE_D_CSV_PATH,
            CASE_E_CSV_PATH,
            CASE_F_CSV_PATH,
        ]

        expected_results = [
            # Case A
            (
                2,
                (
                    datetime.strptime("2026-02-25 09:12:00", DATE_TIME_FORMAT),
                    datetime.strptime("2026-03-01 09:00:00", DATE_TIME_FORMAT),
                ),
            ),
            # Case B
            (1, None),
            # Case C
            (0, None),
            # Case D
            (1, None),
            # Case E
            (
                2,
                (
                    datetime.strptime("2026-03-15 20:10:00", DATE_TIME_FORMAT),
                    datetime.strptime("2026-03-20 12:00:00", DATE_TIME_FORMAT),
                ),
            ),
            # Case F
            (2, None),
        ]

        with open(REGISTERED_CSV_PATH) as registered_file:
            db = Transaction_Database(Test_Transaction_Database.TEMP)
            result = db.add_transactions(registered_file)

            expected_result = (5, None)
            assert result == expected_result, f"""Adding initial data incorrectly:
                Expected result: {expected_result}
                Returned result: {result}
            """

            assert db.dt.equals(db.dt.sort_values(Transaction.START_DATE)), (
                "Sorting fails in initial data addition"
            )

        remove(Test_Transaction_Database.TEMP)

        for case, expected_result in zip(cases, expected_results):
            with open(case) as case_file, open(REGISTERED_CSV_PATH) as registered_file:
                db = Transaction_Database(Test_Transaction_Database.TEMP)
                db.add_transactions(registered_file)

                result = db.add_transactions(case_file)

                assert (
                    result == expected_result
                ), f"""Expected result does not match result in {case}:
                    Expected result: {expected_result}
                    Returned result: {result}
                """

                assert_all_transactions_added(db, REGISTERED_CSV_PATH, case)

                remove(Test_Transaction_Database.TEMP)
