import pytest
import numpy as np
from utils.calculations import (calculate_portfolio_return, 
                              simulate_portfolio_growth,
                              calculate_net_cashflow,
                              get_total_income)
from utils.constraints import DEFAULT_VALUES, ASSET_CLASSES

def test_deterministic_portfolio():
    """Test portfolio with zero volatility and equal returns"""
    test_data = {
        "asset_allocation": {
            "stocks": 0.5,
            "bonds": 0.5,
            "commodities": 0.0,
            "gold": 0.0,
            "foreign_stocks": 0.0,
            "international_bonds": 0.0
        },
        "mean_returns": [0.05, 0.05, 0.0, 0.0, 0.0, 0.0],
        "volatility": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "correlation_matrix": [[1.0 for _ in range(6)] for _ in range(6)],
        "starting_portfolio": 1000000,
        "planning_horizon": 10,
        "age": 45,
        "default_expenses": 50000,
        "default_income": 0,
        "social_security_age": 67,
        "social_security_amount": 0,
        "inflation_rate": 0.0,
        "expense_growth_rate": 0.0,
        "income_growth_rate": 0.0,
        "num_simulations": 100
    }

    paths = simulate_portfolio_growth(test_data)

    # With 5% return and $50,000 withdrawal, after one year should be:
    # 1,000,000 * 1.05 - 50,000 = 1,000,000
    expected_value = 1000000
    for year in range(10):
        expected_value = expected_value * 1.05 - 50000
        assert np.allclose(paths[:, year], expected_value)

def test_social_security_transition():
    """Test portfolio behavior around social security transition"""
    test_data = {
        "asset_allocation": {"stocks": 1.0, "bonds": 0.0, "commodities": 0.0,
                           "gold": 0.0, "foreign_stocks": 0.0, "international_bonds": 0.0},
        "mean_returns": [0.0] * 6,  # Zero returns for deterministic testing
        "volatility": [0.0] * 6,
        "correlation_matrix": [[1.0 for _ in range(6)] for _ in range(6)],
        "starting_portfolio": 1000000,
        "planning_horizon": 25,
        "age": 65,
        "default_expenses": 50000,
        "default_income": 0,
        "social_security_age": 67,
        "social_security_amount": 30000,
        "inflation_rate": 0.0,
        "expense_growth_rate": 0.0,
        "income_growth_rate": 0.0
    }

    # Before SS: withdrawal = 50000
    # After SS: withdrawal = 20000 (50000 - 30000)
    pre_ss_cashflow = calculate_net_cashflow(1, test_data)
    assert pre_ss_cashflow == 50000

    # Test after SS kicks in
    post_ss_cashflow = calculate_net_cashflow(3, test_data)
    assert post_ss_cashflow == 20000

def test_custom_parameters():
    """Test portfolio with custom returns, volatilities, and correlations"""
    test_data = {
        "asset_allocation": {
            "stocks": 0.4,
            "bonds": 0.3,
            "commodities": 0.1,
            "gold": 0.1,
            "foreign_stocks": 0.05,
            "international_bonds": 0.05
        },
        "mean_returns": [0.08, 0.04, 0.06, 0.03, 0.07, 0.035],
        "volatility": [0.15, 0.06, 0.20, 0.15, 0.17, 0.08],
        "correlation_matrix": [
            [1.0, 0.2, 0.3, 0.1, 0.7, 0.2],
            [0.2, 1.0, 0.1, 0.0, 0.2, 0.8],
            [0.3, 0.1, 1.0, 0.4, 0.3, 0.1],
            [0.1, 0.0, 0.4, 1.0, 0.1, 0.0],
            [0.7, 0.2, 0.3, 0.1, 1.0, 0.2],
            [0.2, 0.8, 0.1, 0.0, 0.2, 1.0]
        ],
        "starting_portfolio": 1000000,
        "num_simulations": 10000
    }

    returns = []
    for _ in range(1000):
        result = calculate_portfolio_return(1000000, test_data)
        returns.append((result / 1000000) - 1)

    # Expected portfolio return = sum(weights * returns)
    expected_return = sum(w * r for w, r in zip(
        list(test_data["asset_allocation"].values()),
        test_data["mean_returns"]
    ))

    avg_return = np.mean(returns)
    assert abs(avg_return - expected_return) < 0.01

def test_invalid_parameters():
    """Test that invalid parameters raise appropriate errors"""

    # Test invalid correlation matrix
    with pytest.raises(ValueError):
        test_data = {
            "asset_allocation": {asset: 1/len(ASSET_CLASSES) for asset in ASSET_CLASSES},
            "correlation_matrix": [[1.0, 0.2], [0.2, 1.0]]  # Wrong size
        }
        calculate_portfolio_return(1000000, test_data)

    # Test invalid volatility length
    with pytest.raises(ValueError):
        test_data = {
            "asset_allocation": {asset: 1/len(ASSET_CLASSES) for asset in ASSET_CLASSES},
            "volatility": [0.15, 0.06]  # Wrong size
        }
        calculate_portfolio_return(1000000, test_data)

def test_inflation_impact():
    """Test the impact of inflation on expenses and social security"""
    test_data = {
        "asset_allocation": {"stocks": 1.0, "bonds": 0.0, "commodities": 0.0,
                           "gold": 0.0, "foreign_stocks": 0.0, "international_bonds": 0.0},
        "mean_returns": [0.0] * 6,
        "volatility": [0.0] * 6,
        "correlation_matrix": [[1.0 for _ in range(6)] for _ in range(6)],
        "starting_portfolio": 1000000,
        "age": 65,
        "default_expenses": 50000,
        "social_security_age": 67,
        "social_security_amount": 30000,
        "inflation_rate": 0.02,
        "expense_growth_rate": 0.02
    }

    # Test inflation impact on expenses after 10 years
    year_10_expenses = 50000 * (1.02**10)
    year_10_ss = 30000 * (1.02**10)

    net_cashflow_year_10 = calculate_net_cashflow(10, test_data)
    expected_cashflow = year_10_expenses - year_10_ss

    assert abs(net_cashflow_year_10 - expected_cashflow) < 0.01