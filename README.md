
# Financial Planning Simulator API

A FastAPI-based financial planning calculator API for testing and educational purposes. This API provides endpoints for cash flow projections and portfolio simulations.

## Features

- Cash flow projection and analysis
- Portfolio growth simulation
- Scenario management
- Rate limiting for API protection
- Comprehensive input validation
- CORS protection with configurable origins

## Getting Started

1. Clone this project on Replit
2. The project will automatically install dependencies using Poetry
3. Run the development server:
   ```
   uvicorn main:app --host 0.0.0.0 --reload
   ```

## API Endpoints

### 1. Cash Flow Projection
```http
POST /forecast-cash-flow/
```
Generate detailed cash flow projections with daily, weekly, monthly, quarterly, and annual aggregations.

### 2. Portfolio Simulation For Early Retirees and Freelancers
```http
POST /simulate
```
Simulate portfolio growth and calculate retirement metrics based on user inputs.

### 3. TODO - Scenario Management
- Save and retrieve simulation scenarios
- Compare different financial planning approaches

## Input Models

### Transaction
- name: String
- amount: Float
- type: one-time/repeating
- frequency: daily/weekly/monthly/quarterly/annual
- start_date: Date
- end_date: Date (optional)

### UserData
- starting_portfolio: Float
- planning_horizon: Integer
- asset_allocation: Dictionary
- custom_expenses: Dictionary
- custom_income: Dictionary
- And more configuration options...

## Response Models

### ProjectionResponse
- daily: List[CashFlowEntry]
- weekly: List[AggregatedCashFlow]
- monthly: List[AggregatedCashFlow]
- quarterly: List[AggregatedCashFlow]
- annual: List[AggregatedCashFlow]

### SimulationResult
- risk_of_depletion: Float
- median_final_portfolio: Float
- portfolio_paths: List[List[Float]]

## Rate Limits
- 15 requests per minute per IP
- 3 requests per second burst limit

## Security Features
- CORS protection
- Trusted host middleware
- HTTPS redirect middleware
- Input validation
- Rate limiting

## Testing
Run the test suite using:
```bash
pytest -v
```

## Disclaimer
This tool is for testing and educational purposes only. The results should not be considered as financial advice.

## Tech Stack
- FastAPI
- Pydantic
- SQLAlchemy
- NumPy
- Pandas
- Poetry

## License
This project is licensed under the MIT License
