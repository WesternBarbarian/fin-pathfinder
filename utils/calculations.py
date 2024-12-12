import numpy as np
from typing import Dict, List, Tuple
from scipy.interpolate import interp1d
from utils.constraints import DEFAULT_MEAN_RETURNS, DEFAULT_VOLATILITY, DEFAULT_CORRELATION, ASSET_CLASSES, DEFAULT_VALUES


def convert_to_future_nominal_value(year: int,
                                    custom_values: Dict[int, float],
                                    default_value: float,
                                    growth_rate: float,
                                    use_interpolation: bool = False) -> float:
    """
    Convert present day values to future nominal values using provided growth rate
    
    Args:
        year: Year for calculation
        custom_values: Dictionary of year:value pairs (in today's dollars)
        default_value: Default value (in today's dollars)
        growth_rate: Total growth rate (including any inflationary effects)
        use_interpolation: Whether to interpolate between custom values
    Returns:
        float: Nominal value for the specified year
    """
    if not custom_values:
        return default_value * (1 + growth_rate)**year

    if year in custom_values:
        base_value = custom_values[year]
        return base_value * (1 + growth_rate)**year

    if not use_interpolation:
        return default_value * (1 + growth_rate)**year

    years = sorted(custom_values.keys())
    values = [custom_values[y] for y in years]

    if year < years[0]:
        return default_value * (1 + growth_rate)**year

    if year > years[-1]:
        last_value = custom_values[years[-1]]
        return last_value * (1 + growth_rate)**year

    interpolator = interp1d(years, values, kind='linear')
    interpolated_value = float(interpolator(year))
    return interpolated_value * (1 + growth_rate)**year


def get_total_income(year: int, user_data: Dict) -> float:
    """
    Calculate total income for a given year
    
    Args:
        year: Year for calculation
        user_data: Dictionary containing income parameters in today's dollars
        
    Returns:
        float: Total income in nominal terms
    """
    # Get base income (converted to nominal)
    base_income = convert_to_future_nominal_value(
        year,
        user_data.get("custom_income", {}),
        user_data.get("default_income", DEFAULT_VALUES["default_income"]),
        user_data.get("income_growth_rate", 0.03),
        use_interpolation=user_data.get("use_income_interpolation", False))
    """
    Add social security if eligible.  The SSA reports ss benefits in real dollars. The rest of our analysis is nominal so we need to inflate by the inflation rate.
    """

    current_age = user_data["age"] + year
    if current_age >= user_data["social_security_age"]:
        # Convert social security to nominal
        inflated_ss = user_data["social_security_amount"] * (
            1 + user_data["inflation_rate"])**year
        return base_income + inflated_ss

    return base_income


def calculate_net_cashflow(year: int, user_data: Dict) -> float:
    """
    Calculate net cashflow for the year (positive = withdrawal, negative = contribution)
    
    Args:
        year: Year for calculation
        user_data: Dictionary containing expenses and income info in today's dollars
        
    Returns:
        float: Net cashflow in nominal terms (positive = withdrawal, negative = contribution)
    """
    # Get expenses in nominal terms for the year
    expenses = convert_to_future_nominal_value(
        year,
        user_data.get("custom_expenses", {}),
        user_data.get("default_expenses", DEFAULT_VALUES["default_expenses"]),
        user_data.get("expense_growth_rate", 0.02),
        use_interpolation=user_data.get("use_expense_interpolation", False))

    # Get income in nominal terms for the year
    income = get_total_income(year, user_data)

    # Return net cashflow (positive = withdrawal, negative = contribution)
    return expenses - income


def calculate_portfolio_return(portfolio_value: float, user_data: Dict) -> float:
    """
    Calculate single period portfolio return using either user-provided or default values
    
    Args:
        portfolio_value: Current portfolio value
        user_data: Dictionary containing user inputs and optionally mean_returns, 
                  volatility, and correlation matrix
    Returns:
        float: Updated portfolio value before withdrawals
    """
    try:
        # Get asset allocation
        asset_allocation = np.array(
            [user_data["asset_allocation"][asset] for asset in ASSET_CLASSES])
        
        # Early validation of correlation matrix size
        correlation_matrix = user_data.get("correlation_matrix", None)
        if correlation_matrix is not None:
            n = len(ASSET_CLASSES)
            if len(correlation_matrix) != n or any(len(row) != n for row in correlation_matrix):
                raise ValueError(
                    f"Correlation matrix must be {n}x{n} to match asset classes")
            correlation_matrix = np.array(correlation_matrix)
        else:
            correlation_matrix = DEFAULT_CORRELATION

        # Get mean returns with detailed error checking
        mean_returns = user_data.get("mean_returns", None)
        if mean_returns is None:
            mean_returns = [DEFAULT_MEAN_RETURNS[asset] for asset in ASSET_CLASSES]
        mean_returns = np.array(mean_returns)

        # Get volatilities with detailed error checking 
        volatilities = user_data.get("volatility", None)
        if volatilities is None:
            volatilities = [DEFAULT_VOLATILITY[asset] for asset in ASSET_CLASSES]
        volatilities = np.array(volatilities)

        # Calculate covariance matrix
        try:
            covariance_matrix = np.outer(volatilities, volatilities) * correlation_matrix
        except Exception as e:
            raise ValueError(f"Failed to calculate covariance matrix: {str(e)}")

        # Calculate nominal return
        try:
            random_returns = np.random.multivariate_normal(mean_returns, covariance_matrix)
            portfolio_return = np.dot(asset_allocation, random_returns)
        except Exception as e:
            raise ValueError(f"Failed to calculate portfolio return: {str(e)}")
            
        return portfolio_value * (1 + portfolio_return)
    except Exception as e:
        raise ValueError(f"Portfolio calculation failed: {str(e)}")


def simulate_portfolio_growth(user_data: Dict) -> np.ndarray:
    """
    Simulates portfolio growth using Monte Carlo simulation

    Args:
        user_data: Dictionary containing:
            - starting_portfolio: Current portfolio value (nominal)
            - planning_horizon: Years to simulate
            - asset_allocation: Portfolio weights
            - mean_returns: Nominal returns (optional)
            - custom_expenses: Future expenses in today's dollars (optional)
            - custom_income: Future income in today's dollars (optional)

    Returns:
        np.ndarray: Matrix of nominal portfolio values over time
                   Shape: (num_simulations, years)
    """
    years = user_data["planning_horizon"]
    starting_portfolio = user_data["starting_portfolio"]
    num_simulations = user_data.get("num_simulations", 1000)

    portfolio_paths = np.zeros((num_simulations, years))

    for sim in range(num_simulations):
        portfolio_value = starting_portfolio
        for year in range(years):
            # Calculate investment returns (nominal)
            portfolio_value = calculate_portfolio_return(
                portfolio_value, user_data)

            # Calculate and apply net cashflow (converted to nominal inside function)
            net_cashflow = calculate_net_cashflow(year, user_data)
            portfolio_value = max(portfolio_value - net_cashflow, 0)

            portfolio_paths[sim, year] = portfolio_value

    return portfolio_paths


def calculate_depletion_risk(portfolio_paths: np.ndarray) -> float:
    """
    Calculate the risk of depletion based on portfolio paths
    
    Args:
        portfolio_paths: A 2D array where each row represents a simulated
                        portfolio path over time (in nominal dollars)
    
    Returns:
        float: The proportion of paths that experienced depletion
    """
    total_paths = portfolio_paths.shape[0]

    if total_paths == 0:
        return 0.0

    # A path is considered depleted if nominal value ever reaches zero
    depletion_flags = np.any(portfolio_paths <= 0, axis=1)
    depletion_count = np.sum(depletion_flags)

    return depletion_count / total_paths
