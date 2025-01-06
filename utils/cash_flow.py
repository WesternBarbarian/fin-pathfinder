
from datetime import date, timedelta
from typing import List, Callable
from dateutil.relativedelta import relativedelta
from models.cash_flow import Transaction, TransactionType, Frequency, CashFlowEntry, AggregatedCashFlow

def apply_transaction(transaction: Transaction, cash_flow: List[float], horizon_start: date, horizon_end: date, multiplier: int, date_to_index):
    effective_start = max(transaction.start_date, horizon_start)
    effective_end = min(transaction.end_date or horizon_end, horizon_end)

    if effective_start > effective_end:
        return

    if transaction.type == TransactionType.one_time:
        idx = date_to_index(effective_start)
        if 0 <= idx < len(cash_flow):
            cash_flow[idx] += transaction.amount * multiplier

    elif transaction.type == TransactionType.repeating:
        current_date = effective_start
        while current_date <= effective_end:
            idx = date_to_index(current_date)
            if 0 <= idx < len(cash_flow):
                cash_flow[idx] += transaction.amount * multiplier
            current_date = get_next_date(current_date, transaction.frequency)

def get_next_date(current_date: date, frequency: Frequency) -> date:
    if frequency == Frequency.daily:
        return current_date + timedelta(days=1)
    elif frequency == Frequency.weekly:
        return current_date + timedelta(weeks=1)
    elif frequency == Frequency.monthly:
        return current_date + relativedelta(months=1)
    elif frequency == Frequency.quarterly:
        return current_date + relativedelta(months=3)
    elif frequency == Frequency.annual:
        return current_date + relativedelta(years=1)
    else:
        raise ValueError(f"Unsupported frequency: {frequency}")

def is_same_period(current_date: date, period: str, period_start: date) -> bool:
    if period == "weekly":
        week_start = period_start
        week_end = week_start + timedelta(days=6)
        return week_start <= current_date <= week_end
    elif period == "monthly":
        return current_date.month == period_start.month and current_date.year == period_start.year
    elif period == "quarterly":
        start_quarter = (period_start.month - 1) // 3 + 1
        current_quarter = (current_date.month - 1) // 3 + 1
        return current_quarter == start_quarter and current_date.year == period_start.year
    elif period == "annual":
        return current_date.year == period_start.year
    return False

def aggregate_cash_flow(daily_entries: List[CashFlowEntry], period: str) -> List[AggregatedCashFlow]:
    if period not in {"weekly", "monthly", "quarterly", "annual"}:
        raise ValueError(f"Unsupported aggregation period: {period}")

    aggregated = []
    temp_revenue = 0.0
    temp_expense = 0.0
    temp_net = 0.0
    period_start = None
    period_end = None

    for entry in daily_entries:
        if period_start is None:
            period_start = entry.date

        if not is_same_period(entry.date, period, period_start):
            aggregated.append(
                AggregatedCashFlow(
                    period=period.capitalize(),
                    start_date=period_start,
                    end_date=period_end,
                    total_revenues=round(temp_revenue, 2),
                    total_expenses=round(temp_expense, 2),
                    net_cash_flow=round(temp_net, 2)
                )
            )
            temp_revenue = 0.0
            temp_expense = 0.0
            temp_net = 0.0
            period_start = entry.date

        temp_revenue += entry.total_revenues
        temp_expense += entry.total_expenses
        temp_net += entry.net_cash_flow
        period_end = entry.date

    if period_start is not None:
        aggregated.append(
            AggregatedCashFlow(
                period=period.capitalize(),
                start_date=period_start,
                end_date=period_end,
                total_revenues=round(temp_revenue, 2),
                total_expenses=round(temp_expense, 2),
                net_cash_flow=round(temp_net, 2)
            )
        )

    return aggregated
