# tests/test_endpoints.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Financial Planning Simulator API is running"}

def test_forecast_cash_flow_basic():
    """Test basic cash flow forecast"""
    request_data = {
        "expenses": [{
            "name": "Rent",
            "amount": 2000.0,
            "type": "repeating",
            "frequency": "monthly",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        }],
        "revenues": [{
            "name": "Salary",
            "amount": 5000.0,
            "type": "repeating",
            "frequency": "monthly",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        }],
        "start_date": "2024-01-01",
        "end_date": "2024-12-31"
    }
    
    response = client.post("/forecast-cash-flow/", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert all(key in data for key in ["daily", "weekly", "monthly", "quarterly", "annual"])
    assert len(data["daily"]) == 366  # 2024 is a leap year
    
def test_forecast_cash_flow_invalid_dates():
    """Test invalid date ranges"""
    request_data = {
        "expenses": [],
        "revenues": [],
        "start_date": "2024-12-31",
        "end_date": "2024-01-01"  # End before start
    }
    
    response = client.post("/forecast-cash-flow/", json=request_data)
    assert response.status_code == 400
    
def test_forecast_cash_flow_one_time():
    """Test one-time transactions"""
    request_data = {
        "expenses": [{
            "name": "Car Purchase",
            "amount": 30000.0,
            "type": "one-time",
            "start_date": "2024-06-15"
        }],
        "revenues": [],
        "start_date": "2024-06-01",
        "end_date": "2024-07-01"
    }
    
    response = client.post("/forecast-cash-flow/", json=request_data)
    assert response.status_code == 200
    data = response.json()
    # Find the specific day with the expense
    day_with_expense = next(
        (day for day in data["daily"] if day["total_expenses"] > 0),
        None
    )
    assert day_with_expense is not None
    assert day_with_expense["date"] == "2024-06-15"
    assert day_with_expense["total_expenses"] == 30000.0

def test_forecast_cash_flow_leap_year():
    """Test handling of leap years"""
    request_data = {
        "expenses": [{
            "name": "Leap Day Expense",
            "amount": 1000.0,
            "type": "one-time",
            "start_date": "2024-02-29"
        }],
        "revenues": [],
        "start_date": "2024-02-01",
        "end_date": "2024-03-01"
    }
    
    response = client.post("/forecast-cash-flow/", json=request_data)
    assert response.status_code == 200
    data = response.json()
    leap_day = next(
        (day for day in data["daily"] if day["date"] == "2024-02-29"),
        None
    )
    assert leap_day is not None
    assert leap_day["total_expenses"] == 1000.0

def test_forecast_cash_flow_invalid_frequency():
    """Test invalid frequency for repeating transaction"""
    request_data = {
        "expenses": [{
            "name": "Invalid",
            "amount": 100.0,
            "type": "repeating",
            "frequency": "invalid_frequency",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        }],
        "revenues": [],
        "start_date": "2024-01-01",
        "end_date": "2024-12-31"
    }
    
    response = client.post("/forecast-cash-flow/", json=request_data)
    assert response.status_code == 400

def test_forecast_cash_flow_aggregation():
    """Test aggregation periods"""
    request_data = {
        "expenses": [{
            "name": "Monthly Expense",
            "amount": 1000.0,
            "type": "repeating",
            "frequency": "monthly",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        }],
        "revenues": [],
        "start_date": "2024-01-01",
        "end_date": "2024-12-31"
    }
    
    response = client.post("/forecast-cash-flow/", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert len(data["monthly"]) == 12
    assert len(data["quarterly"]) == 4
    assert len(data["annual"]) == 1

def test_simulate():
    """Test the simulation endpoint with valid data"""
    test_data = {
        "starting_portfolio": 5000000,
        "planning_horizon": 40,
        "age": 45,
        "default_expenses": 50000,
        "default_income": 0,
        "social_security_age": 67,
        "social_security_amount": 10000,
        "inflation_rate": 0.02,
        "num_simulations": 1000,
        "expense_growth_rate": 0.02,
        "income_growth_rate": 0.03,
        "asset_allocation": {
            "stocks": 0.5,
            "bonds": 0.5,
            "commodities": 0.0,
            "gold": 0.0,
            "foreign_stocks": 0.0,
            "international_bonds": 0.0
        }
    }
    
    response = client.post("/simulate", json=test_data)
    assert response.status_code == 200
    result = response.json()
    
    # Check if all required fields are in the response
    assert all(key in result for key in [
        "risk_of_depletion",
        "median_final_portfolio",
        "portfolio_paths"
    ])