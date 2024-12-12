# tests/test_endpoints.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Financial Planning Simulator API is running"}

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