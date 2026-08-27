from __future__ import annotations

from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Iterable

import altair as alt
import pandas as pd
import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile

from src.entities.time_granularity import Time_Granularity
from src.services.analytics.activity import get_grouped_incomes_outcomes
from src.storage.models.transaction import Transaction
from src.storage.transaction_database import Transaction_Database


APP_NAME = "Revolut Helper"
GRANULARITY_OPTIONS = {
    "Day": Time_Granularity.DAY,
    "Week": Time_Granularity.WEEK,
    "Month": Time_Granularity.MONTH,
    "Year": Time_Granularity.YEAR,
}
ACTIVITY_COLUMNS = ["date", "income", "spending", "net", "balance"]


if "db" not in st.session_state:
    st.session_state.db = Transaction_Database()

if "uploaded_file_ids" not in st.session_state:
    st.session_state.uploaded_file_ids = set()

if "upload_messages" not in st.session_state:
    st.session_state.upload_messages = []


db: Transaction_Database = st.session_state.db


# -----------------------------
# Data helpers
# -----------------------------
def available_transactions() -> pd.DataFrame:
    if db.dt.empty:
        return db.dt.copy()

    transactions = db.dt.copy()
    transactions[Transaction.START_DATE] = pd.to_datetime(
        transactions[Transaction.START_DATE]
    )
    return transactions.sort_values(Transaction.START_DATE).reset_index(drop=True)


def data_date_bounds(transactions: pd.DataFrame) -> tuple[date, date]:
    if transactions.empty:
        today = date.today()
        return today - timedelta(days=30), today

    started_dates = pd.to_datetime(transactions[Transaction.START_DATE])
    return started_dates.min().date(), started_dates.max().date()


def normalize_date_range(
    selected_range: date | Iterable[date],
) -> tuple[date, date] | None:
    # NOTE: Ok but maybe just allow date range in the future to simplify
    if isinstance(selected_range, date):
        return selected_range, selected_range

    selected_dates = list(selected_range)
    if len(selected_dates) == 0:
        return None
    if len(selected_dates) == 1:
        return selected_dates[0], selected_dates[0]

    start_date, end_date = selected_dates[0], selected_dates[1]
    if start_date > end_date:
        return end_date, start_date
    return start_date, end_date


def load_activity_data(
    start_date: date, end_date: date, granularity: Time_Granularity
) -> tuple[pd.DataFrame, str | None]:
    # NOTE: Strange, why are we turning the data again to a pandas dataframe?
    start_datetime = datetime.combine(start_date, time.min)
    end_datetime = datetime.combine(end_date, time.max)

    result = get_grouped_incomes_outcomes(
        db=db,
        start_date=start_datetime,
        end_date=end_datetime,
        granularity=granularity,
    )
    if not result.ok:
        return pd.DataFrame(columns=ACTIVITY_COLUMNS), result.error

    assert result.data is not None
    rows = [
        {
            "date": row.start_date,
            "income": row.positive_sum,
            "spending": abs(row.negative_sum),
            "net": row.positive_sum + row.negative_sum,
            "balance": row.balance,
        }
        for row in result.data
    ]
    return pd.DataFrame(rows, columns=ACTIVITY_COLUMNS), None


def transactions_between(
    transactions: pd.DataFrame, start_date: date, end_date: date
) -> pd.DataFrame:
    if transactions.empty:
        return transactions.copy()

    start_datetime = datetime.combine(start_date, time.min)
    end_datetime = datetime.combine(end_date, time.max)
    mask = transactions[Transaction.START_DATE].between(start_datetime, end_datetime)
    return transactions[mask].copy()  # type: ignore[reportReturnType]


def current_balance(transactions: pd.DataFrame) -> float | None:
    if transactions.empty:
        return None
    return float(transactions.iloc[-1][Transaction.BALANCE])


def euro(amount: float | int | None) -> str:
    if amount is None:
        return "—"
    return f"€{amount:,.2f}"


def format_gap(gap: tuple[datetime, datetime] | None) -> str:
    if gap is None:
        return ""

    gap_start, gap_end = gap
    return f" Gap detected from {gap_start:%d %b %Y} to {gap_end:%d %b %Y}."


def handle_uploaded_files(uploaded_files: list[UploadedFile]) -> list[str]:
    messages: list[str] = []
    uploaded_ids = st.session_state.uploaded_file_ids

    for uploaded_file in uploaded_files:
        if uploaded_file.file_id in uploaded_ids:
            continue

        try:
            uploaded_file.seek(0)
            added_count, gap = db.add_transactions(uploaded_file)
        except Exception as error:  # noqa: BLE001 - Streamlit should show upload failures.
            messages.append(f"Could not import {uploaded_file.name}: {error}")
            continue

        uploaded_ids.add(uploaded_file.file_id)
        if added_count == 0:
            messages.append(f"{uploaded_file.name}: no new transactions found.")
        else:
            messages.append(
                f"{uploaded_file.name}: imported {added_count} transaction(s)."
                f"{format_gap(gap)}"
            )

    st.session_state.uploaded_file_ids = uploaded_ids
    st.session_state.upload_messages = messages
    return messages


# -----------------------------
# UI helpers
# -----------------------------
def inject_styles() -> None:
    style_path = Path(__file__).parent / "assets" / "style.css"
    if style_path.exists():
        st.markdown(
            f"<style>{style_path.read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True,
        )


def render_title() -> None:
    st.markdown(
        '<h1 class="app-title">Revolut Helper</h1>',
        unsafe_allow_html=True,
    )


def render_upload_button() -> None:
    with st.popover("Import", use_container_width=True):
        st.caption("Upload Revolut CSV exports. Existing transactions are skipped.")
        uploaded_files = st.file_uploader(
            "Revolut CSV files",
            type=["csv"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )
        if uploaded_files:
            messages = handle_uploaded_files(uploaded_files)
            for message in messages:
                if message.startswith("Could not"):
                    st.toast(message, icon=":material/error:")
                else:
                    st.toast(message, icon=":material/check_circle:")


def render_upload_feedback() -> None:
    if not st.session_state.upload_messages:
        return

    for message in st.session_state.upload_messages:
        if message.startswith("Could not"):
            st.error(message)
        else:
            st.success(message)


def build_activity_chart(data: pd.DataFrame) -> alt.Chart:
    if data.empty:
        placeholder = pd.DataFrame({"date": [], "metric": [], "amount": []})
        return (
            alt.Chart(placeholder)
            .mark_bar()
            .encode(
                x=alt.X("date:T", title="Date"),
                y=alt.Y("amount:Q", title="Amount"),
            )
            .properties(height=520)
        )

    bars = data.melt(
        id_vars=["date"],
        value_vars=["income", "spending"],
        var_name="metric",
        value_name="amount",
    )

    cash_flow = (
        alt.Chart(bars)
        .mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5, opacity=0.82)
        .encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("amount:Q", title="Cash flow"),
            color=alt.Color(
                "metric:N",
                title="",
                scale=alt.Scale(
                    domain=["income", "spending"],
                    range=["#34c759", "#ff453a"],
                ),
            ),
            tooltip=[
                alt.Tooltip("date:T", title="Period"),
                alt.Tooltip("metric:N", title="Type"),
                alt.Tooltip("amount:Q", title="Amount", format=",.2f"),
            ],
        )
    )

    balance = (
        alt.Chart(data)
        .mark_line(point=True, color="#0a84ff", strokeWidth=3)
        .encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("balance:Q", title="Balance"),
            tooltip=[
                alt.Tooltip("date:T", title="Period"),
                alt.Tooltip("income:Q", title="Income", format=",.2f"),
                alt.Tooltip("spending:Q", title="Spending", format=",.2f"),
                alt.Tooltip("net:Q", title="Net", format=",.2f"),
                alt.Tooltip("balance:Q", title="Balance", format=",.2f"),
            ],
        )
    )

    return (  # type: ignore[reportReturnType]
        alt.layer(cash_flow, balance)
        .resolve_scale(y="independent")
        .properties(height=520)
        .configure_axis(labelColor="#536579", titleColor="#536579", gridColor="#e8eef7")
        .configure_view(strokeWidth=0)
        .configure_legend(orient="top", labelColor="#24364b")
    )


def render_metrics(
    activity_data: pd.DataFrame, filtered_transactions: pd.DataFrame
) -> None:
    total_income = (
        float(activity_data["income"].sum()) if not activity_data.empty else 0.0  # type: ignore[reportReturnType]
    )
    total_spending = (
        float(activity_data["spending"].sum()) if not activity_data.empty else 0.0  # type: ignore[reportReturnType]
    )
    net = total_income - total_spending
    balance = current_balance(filtered_transactions)

    cols = st.columns(4)
    cols[0].metric("Current balance", euro(balance))
    cols[1].metric("Income", euro(total_income))
    cols[2].metric("Spending", euro(total_spending))
    cols[3].metric("Net", euro(net), delta=euro(net))


def render_transactions_table(transactions: pd.DataFrame) -> None:
    if transactions.empty:
        st.info("No transactions found for this period.")
        return

    visible_columns = [
        Transaction.START_DATE,
        Transaction.DESCRIPTION,
        Transaction.AMOUNT,
        Transaction.FEE,
        Transaction.CURRENCY,
        Transaction.STATE,
        Transaction.BALANCE,
    ]
    table_data = transactions[visible_columns].sort_values(  # type: ignore[reportCallIssue]
        by=Transaction.START_DATE,
        ascending=False,
    )
    st.dataframe(
        table_data,
        width="stretch",
        hide_index=True,
        column_config={
            Transaction.START_DATE: st.column_config.DatetimeColumn(
                "Date", format="DD MMM YYYY, HH:mm"
            ),
            Transaction.DESCRIPTION: st.column_config.TextColumn("Description"),
            Transaction.AMOUNT: st.column_config.NumberColumn("Amount", format="€%.2f"),
            Transaction.FEE: st.column_config.NumberColumn("Fee", format="€%.2f"),
            Transaction.BALANCE: st.column_config.NumberColumn(
                "Balance", format="€%.2f"
            ),
        },
    )


# -----------------------------
# App
# -----------------------------
st.set_page_config(page_title=APP_NAME, layout="wide")
inject_styles()

all_transactions = available_transactions()
earliest_date, latest_date = data_date_bounds(all_transactions)
default_start_date, default_end_date = (
    max(earliest_date, latest_date - timedelta(days=90)),
    latest_date,
)

top_cols = st.columns([1.8, 2.5, 1, 0.9], vertical_alignment="bottom")
with top_cols[0]:
    render_title()
with top_cols[1]:
    selected_range = st.date_input(
        "Date range",
        value=(default_start_date, default_end_date),
        min_value=earliest_date,
        max_value=max(latest_date, date.today()),
    )
with top_cols[2]:
    selected_granularity = st.selectbox(
        "Group by",
        options=list(GRANULARITY_OPTIONS.keys()),
        index=2 if (default_end_date - default_start_date).days > 60 else 0,
    )
with top_cols[3]:
    render_upload_button()

render_upload_feedback()

normalized_range = normalize_date_range(selected_range)
if normalized_range is None:
    st.warning("Select a start and end date to continue.")
    st.stop()

start_date, end_date = normalized_range
activity_data, activity_error = load_activity_data(
    start_date, end_date, GRANULARITY_OPTIONS[selected_granularity]
)
filtered_transactions = transactions_between(all_transactions, start_date, end_date)

if activity_error:
    st.error(activity_error)
    st.stop()

render_metrics(activity_data, filtered_transactions)

chart_tab, transactions_tab = st.tabs(["Activity", "Transactions"])
with chart_tab:
    if activity_data.empty:
        st.info(
            "No chart data for this range. Try widening the date range or importing a CSV."
        )
    st.altair_chart(build_activity_chart(activity_data), width="stretch")

with transactions_tab:
    render_transactions_table(filtered_transactions)
