# Financial Planning Simulator API

A FastAPI-based financial planning calculator API for testing and educational purposes. This API provides endpoints for cash flow projections and portfolio simulations.

Front-end: https://lifebeyondthe9to5.com

## LEGAL DISCLAIMER

THIS SOFTWARE IS PROVIDED FOR EDUCATIONAL AND TESTING PURPOSES ONLY. 

- This is NOT financial advice
- I am NOT a financial planner, advisor, or registered investment professional
- The calculations and projections provided are purely for educational purposes
- Any results or projections should not be considered as financial or investment advice
- You should consult with qualified financial professionals for actual financial planning and investment decisions
- This software is provided "AS IS" without any warranties or guarantees
- The creator(s) assume no responsibility for any financial decisions made based on this tool

## Features

- Cash flow projection and analysis
- Portfolio simulation
- Rate limiting for API protection
- Input validation
- CORS protection with configurable origins

## Getting Started

1. Clone this repository and navigate to the project directory:
   ```bash
   git clone https://github.com/username/project-name
   cd project-name
   ```

2. Install required dependencies from pyproject.toml:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the development server:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

The API will be available at `http://0.0.0.0:8000`. You can access the interactive API documentation at `http://0.0.0.0:8000/docs`.

### CORS Configuration
By default, the API allows requests from:
- https://lifebeyondthe9to5.com
- http://localhost:3000
- Replit domains (*.replit.dev|app|co)

If you need to allow different origins, modify the ALLOWED_ORIGINS and ALLOWED_REGEX constants in main.py.

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

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

This means you can:
- Use this code commercially
- Modify the code
- Distribute the code
- Use it privately
- Sublicense the code

The only requirement is including the original license and copyright notice in any copy of the software/source.