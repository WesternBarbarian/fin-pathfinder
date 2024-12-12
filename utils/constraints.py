import numpy as np

# Default simulation parameters
DEFAULT_NUM_SIMULATIONS = 1000

# Default return assumptions (mean annual returns)
DEFAULT_MEAN_RETURNS = {
    "stocks": 0.09,         # Changed from 0.07 to include inflation
    "bonds": 0.066,         # Changed from 0.046 to include inflation
    "commodities": 0.055,   # Changed from 0.035 to include inflation
    "gold": 0.05,          # Changed from 0.03 to include inflation
    "foreign_stocks": 0.094,# Changed from 0.074 to include inflation
    "international_bonds": 0.065  # Changed from 0.045 to include inflation
}

"""
Note: 
- All return assumptions are in nominal terms (including inflation)
- Custom expenses/income should be specified in today's dollars
- Default volatility and correlation matrices remain unchanged as they're relatively stable
"""

# Default volatility matrix (standard deviations)
DEFAULT_VOLATILITY = {
    "stocks": 0.15,
    "bonds": 0.138,
    "commodities": 0.167,
    "gold": 0.10,
    "foreign_stocks": 0.179,
    "international_bonds": 0.148
}

# Asset classes
ASSET_CLASSES = list(DEFAULT_MEAN_RETURNS.keys())

# Default correlation matrix
DEFAULT_CORRELATION = np.array([
    [1.00, 0.22, 0.12, 0.10, 0.85, 0.20],  # Stocks
    [0.22, 1.00, 0.15, 0.05, 0.30, 0.80],  # Bonds
    [0.12, 0.15, 1.00, 0.25, 0.20, 0.15],  # Commodities
    [0.10, 0.05, 0.25, 1.00, 0.15, 0.10],  # Gold
    [0.85, 0.30, 0.20, 0.15, 1.00, 0.35],  # Foreign Stocks
    [0.20, 0.80, 0.15, 0.10, 0.35, 1.00],  # International Bonds
])

# Other default values
DEFAULT_VALUES = {
    "starting_portfolio": 1700000,
    "planning_horizon": 40,
    "age": 45,
    "default_expenses": 50000,
    "default_income": 0,
    "social_security_age": 67,
    "social_security_amount": 10000,
    "inflation_rate": 0.02,
    "num_simulations": DEFAULT_NUM_SIMULATIONS,
    "expense_growth_rate": 0.02,  # 2% annual growth by default
    "income_growth_rate": 0.03,   # 3% annual growth by default
}


VALIDATION_LIMITS = {
    "portfolio": {"min": 0, "max": 100_000_000},  # $100M max
    "horizon": {"min": 1, "max": 100},            # 100 years max
    "age": {"min": 10, "max": 100},              # Age limits
    "expenses": {"min": 0, "max": 10_000_000},   # $10M annual max
    "income": {"min": 0, "max": 10_000_000},     # $10M annual max
    "simulations": {"min": 100, "max": 10000},   # Simulation count limits
    "rate": {"min": -0.1, "max": 0.15},          # Rate limits (-10% to 15%)
}