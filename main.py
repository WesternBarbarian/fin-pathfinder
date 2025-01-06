from typing import List
from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from datetime import date, timedelta
from models.cash_flow import (
    ProjectionRequest,
    ProjectionResponse,
    CashFlowEntry,
    Transaction
)
from utils.cash_flow import apply_transaction, aggregate_cash_flow
from starlette.exceptions import ExceptionMiddleware
from fastapi.responses import JSONResponse
from utils.exceptions import (
    ErrorResponse,
    FinancialPlannerException,
    ValidationError
) 
from utils.validation import validate_asset_allocation
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from models.schemas import (UserData, SimulationResult)
from utils.calculations import simulate_portfolio_growth, calculate_depletion_risk
import numpy as np
import traceback


# Initialize FastAPI and rate limiter
app = FastAPI(
    title="Financial Planning Simulator API",
    description="A financial planning calculator API for testing purposes only. Not financial advice.",
    version="0.5.0",
)
# Create limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
# Rate limit constants
RATE_LIMIT = "15/minute"
BURST_LIMIT = "3/second"

# CORS configuration
ALLOWED_ORIGINS = [
    "https://lifebeyondthe9to5.com",
    "http://localhost:3000"
]
ALLOWED_REGEX = r"https://.*\.replit\.(dev|app|co)$"

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=ALLOWED_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
@limiter.limit(RATE_LIMIT)  # Allow 15 requests per minute per IP
@limiter.limit(BURST_LIMIT)
async def root(request: Request):
    return {"message": "Financial Planning Simulator API is running"}

@app.post("/projection/", response_model=ProjectionResponse)
@limiter.limit(RATE_LIMIT)
@limiter.limit(BURST_LIMIT)
async def generate_projection(request: Request, data: ProjectionRequest):
    """Generate cash flow projection over specified planning horizon"""
    if data.start_date > data.end_date:
        raise HTTPException(status_code=400, detail="start_date cannot be after end_date.")

    total_days = (data.end_date - data.start_date).days + 1
    revenues_daily = [0.0 for _ in range(total_days)]
    expenses_daily = [0.0 for _ in range(total_days)]

    def date_to_index(d: date) -> int:
        return (d - data.start_date).days

    for transaction in data.revenues + data.expenses:
        multiplier = 1 if transaction in data.revenues else -1
        try:
            apply_transaction(
                transaction,
                revenues_daily if multiplier == 1 else expenses_daily,
                data.start_date,
                data.end_date,
                multiplier,
                date_to_index
            )
        except ValueError as ve:
            raise HTTPException(status_code=400, detail=str(ve))

    daily_entries = [
        CashFlowEntry(
            date=data.start_date + timedelta(days=i),
            total_revenues=round(revenues_daily[i], 2),
            total_expenses=round(abs(expenses_daily[i]), 2),
            net_cash_flow=round(revenues_daily[i] + expenses_daily[i], 2)
        )
        for i in range(total_days)
    ]

    return ProjectionResponse(
        daily=daily_entries,
        weekly=aggregate_cash_flow(daily_entries, "weekly"),
        monthly=aggregate_cash_flow(daily_entries, "monthly"),
        quarterly=aggregate_cash_flow(daily_entries, "quarterly"),
        annual=aggregate_cash_flow(daily_entries, "annual")
    )

@app.exception_handler(FinancialPlannerException)
async def financial_planner_exception_handler(
    request: Request,
    exc: FinancialPlannerException
):
    error_response = ErrorResponse(
        status_code=exc.status_code,
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )


@app.exception_handler(HTTPException)
async def cors_error_handler(request: Request, exc: HTTPException):
    if exc.status_code == 403:  # Forbidden - CORS error
        error_response = ErrorResponse(
            status_code=403,
            error_code="CORS_ERROR",
            message="Origin not allowed",
            details={
                "allowed_origins": ALLOWED_ORIGINS,
                "allowed_pattern": ALLOWED_REGEX
            }
        )
        return JSONResponse(
            status_code=403,
            content=error_response.model_dump()
        )
    raise exc


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    retry_after = exc.headers.get('Retry-After', '60')  # Default to 60 seconds if not specified
    
    error_response = ErrorResponse(
        status_code=429,
        error_code="RATE_LIMIT_EXCEEDED",
        message="Too many requests. Please try again later.",
        details={
            "retry_after": retry_after
        }
    )
    return JSONResponse(
        status_code=429,
        content=error_response.model_dump()
    )
@app.exception_handler(Exception)
async def general_exception_handler(request: Request,exc: Exception):
    error_response = ErrorResponse(
        status_code=500,
        error_code="INTERNAL_SERVER_ERROR",
        message="An unexpected error occurred",
        details={
            "error": str(exc),
            "trace": traceback.format_exc() if app.debug else None
        }
    )
    return JSONResponse(
        status_code=500,
        content=error_response.model_dump()
    )

@app.post("/simulate", response_model=SimulationResult)
@limiter.limit(RATE_LIMIT)
@limiter.limit(BURST_LIMIT)

async def simulate(request: Request, user_data: UserData):
    """Simulate portfolio growth and calculate retirement metrics"""
    try:
        # Validate asset allocation
        if not user_data.asset_allocation:
            raise ValidationError(
                message="Asset allocation is required",
                details={
                    "field": "asset_allocation",
                    "constraint": "must not be empty"
                }
            )

        # Validate numeric inputs
        if user_data.starting_portfolio <= 0:
            raise ValidationError(
                message="Starting portfolio must be greater than 0",
                details={
                    "field": "starting_portfolio",
                    "constraint": "must be positive",
                    "provided_value": user_data.starting_portfolio
                }
            )

        if user_data.planning_horizon <= 0:
            raise ValidationError(
                message="Planning horizon must be greater than 0",
                details={
                    "field": "planning_horizon",
                    "constraint": "must be positive",
                    "provided_value": user_data.planning_horizon
                }
            )

        # Run simulation
        try:
            portfolio_paths = simulate_portfolio_growth(user_data.model_dump())
        except Exception as e:
            raise SimulationError(
                message="Portfolio simulation failed",
                details={
                    "error": str(e),
                    "simulation_parameters": user_data.model_dump()
                }
            )

        # Calculate results
        try:
            risk = calculate_depletion_risk(portfolio_paths)
            final_median = np.median(portfolio_paths[:, -1])
        except Exception as e:
            raise SimulationError(
                message="Error calculating simulation results",
                details={
                    "error": str(e),
                    "calculation_stage": "final_metrics"
                }
            )

        return SimulationResult(
            risk_of_depletion=risk,
            median_final_portfolio=final_median,
            portfolio_paths=portfolio_paths.tolist()
        )

    except (ValidationError, SimulationError) as e:
        raise e
    except Exception as e:
        raise SimulationError(
            message="Unexpected simulation error",
            details={"error": str(e)}
        )
