
from pydantic import BaseModel, Field, field_validator
from datetime import date
from typing import List, Optional
from enum import Enum

class TransactionType(str, Enum):
    one_time = "one-time"
    repeating = "repeating"

class Frequency(str, Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    quarterly = "quarterly"
    annual = "annual"

class Transaction(BaseModel):
    name: str = Field(..., example="Salary Payment")
    amount: float = Field(..., example=5000.0, gt=0)
    type: TransactionType = Field(..., example="repeating")
    frequency: Optional[Frequency] = Field(None, example="monthly")
    start_date: date = Field(..., example="2025-01-01")
    end_date: Optional[date] = Field(None, example="2025-12-31")

    @field_validator("frequency")
    def validate_frequency(cls, v, values, **kwargs):
        transaction_type = values.get('type')
        if transaction_type == TransactionType.repeating:
            if not v:
                raise ValueError("Frequency is required for repeating transactions.")
        else:
            if v is not None:
                raise ValueError("Frequency should not be set for one-time transactions.")
        return v

    @field_validator("end_date")
    def validate_dates(cls, v, values, **kwargs):
        start = values.get('start_date')
        if v and start and v < start:
            raise ValueError("end_date cannot be before start_date.")
        return v

class ProjectionRequest(BaseModel):
    expenses: List[Transaction] = Field(default_factory=list)
    revenues: List[Transaction] = Field(default_factory=list)
    start_date: date = Field(..., example="2025-01-01")
    end_date: date = Field(..., example="2025-12-31")

    @field_validator("end_date")
    def validate_horizon(cls, v, values):
        start = values.get("start_date")
        if start and v < start:
            raise ValueError("end_date cannot be before start_date.")
        return v

class CashFlowEntry(BaseModel):
    date: date
    total_revenues: float
    total_expenses: float
    net_cash_flow: float

class AggregatedCashFlow(BaseModel):
    period: str
    start_date: date
    end_date: date
    total_revenues: float
    total_expenses: float
    net_cash_flow: float

class ProjectionResponse(BaseModel):
    daily: List[CashFlowEntry]
    weekly: List[AggregatedCashFlow]
    monthly: List[AggregatedCashFlow]
    quarterly: List[AggregatedCashFlow]
    annual: List[AggregatedCashFlow]
