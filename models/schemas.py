from pydantic import BaseModel, field_validator
from typing import Dict, List, Optional
from utils.validation import validate_asset_allocation, validate_numeric_input
from utils.constraints import DEFAULT_VALUES, ASSET_CLASSES
from utils.exceptions import ValidationError


class UserData(BaseModel):
    starting_portfolio: float = DEFAULT_VALUES["starting_portfolio"]
    planning_horizon: int = DEFAULT_VALUES["planning_horizon"]
    age: int = DEFAULT_VALUES["age"]
    default_expenses: float = DEFAULT_VALUES["default_expenses"]
    default_income: float = DEFAULT_VALUES["default_income"]
    custom_expenses: Dict[int, float] = {}  # year to expense amount mapping
    custom_income: Dict[int, float] = {}  # year to income amount mapping
    social_security_age: int = DEFAULT_VALUES["social_security_age"]
    social_security_amount: float = DEFAULT_VALUES["social_security_amount"]
    inflation_rate: float = DEFAULT_VALUES["inflation_rate"]
    num_simulations: int = DEFAULT_VALUES["num_simulations"]
    expense_growth_rate: float = DEFAULT_VALUES["expense_growth_rate"]
    income_growth_rate: float = DEFAULT_VALUES["income_growth_rate"]
    asset_allocation: Dict[str, float] = {asset: 1/len(ASSET_CLASSES) for asset in ASSET_CLASSES}  # Equal weight by default
    mean_returns: Optional[List[float]] = [DEFAULT_MEAN_RETURNS[asset] for asset in ASSET_CLASSES]
    volatility: Optional[List[float]] = [DEFAULT_VOLATILITY[asset] for asset in ASSET_CLASSES]
    correlation_matrix: Optional[List[List[float]]] = DEFAULT_CORRELATION.tolist()
    use_expense_interpolation: bool = False
    use_income_interpolation: bool = False

    @field_validator('asset_allocation')
    def validate_allocation(cls, v):
        try:
            validate_asset_allocation(v)
            return v
        except ValidationError as e:
            raise ValueError(e.message)

    @field_validator('starting_portfolio')
    def validate_portfolio(cls, v):
        validate_numeric_input(v, "portfolio")
        return v

    @field_validator('planning_horizon')
    def validate_horizon(cls, v):
        validate_numeric_input(v, "horizon")
        return v

    @field_validator('age')
    def validate_age(cls, v):
        validate_numeric_input(v, "age")
        return v

    @field_validator('default_expenses')
    def validate_expenses(cls, v):
        validate_numeric_input(v, "expenses")
        return v

    @field_validator('num_simulations')
    def validate_simulations(cls, v):
        validate_numeric_input(v, "simulations")
        return v

    @field_validator('inflation_rate', 'expense_growth_rate',
                     'income_growth_rate')
    def validate_rates(cls, v):
        validate_numeric_input(v, "rate")
        return v

    @field_validator('volatility')
    def validate_volatility(cls, v):
        if v is not None and len(v) != len(ASSET_CLASSES):
            raise ValidationError(
                detail=
                f"Volatility list must match number of asset classes ({len(ASSET_CLASSES)})"
            )
        return v

    @field_validator('correlation_matrix')
    def validate_correlation(cls, v):
        if v is not None:
            if not isinstance(v, list) or not all(
                    isinstance(row, list) for row in v):
                raise ValidationError(
                    detail="Correlation matrix must be a 2D list")
            n = len(ASSET_CLASSES)
            if len(v) != n or any(len(row) != n for row in v):
                raise ValidationError(
                    detail=
                    f"Correlation matrix must be {n}x{n} to match asset classes"
                )
        return v


class SimulationResult(BaseModel):
    disclaimer: str = "Tool is for testing only. Results are not financial advice."
    risk_of_depletion: float
    median_final_portfolio: float
    portfolio_paths: List[List[float]]  # 2D list for JSON serialization
