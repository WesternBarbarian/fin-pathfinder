import numpy as np
from typing import Any, Dict
from utils.constraints import VALIDATION_LIMITS
from utils.exceptions import ValidationError

def validate_asset_allocation(allocation: dict) -> bool:
    """Validate that asset allocation sums to 100%"""
    total = sum(allocation.values())
    if not abs(total - 1.0) < 0.0001:  # Using small epsilon for float comparison
        raise ValidationError(
            message="Asset allocation must sum to 1.0 (100%)",
            details={
                "current_sum": f"{total:.2%}",
                "allocation": allocation
            }
        )
    return True


def validate_numeric_input(value: float, field_name: str) -> bool:
    """Validates numeric inputs against predefined limits"""
    if field_name not in VALIDATION_LIMITS:
        raise ValidationError(
            message=f"Unknown field: {field_name}",
            details={"field": field_name}
        )
    limits = VALIDATION_LIMITS[field_name]
    if not isinstance(value, (int, float)):
        raise ValidationError(
            message=f"{field_name} must be a number",
            details={
                "field": field_name,
                "type": type(value).__name__,
                "expected_type": "number"
            }
        )
    if value < limits["min"] or value > limits["max"]:
        raise ValidationError(
            message=f"{field_name} must be between {limits['min']} and {limits['max']}",
            details={
                "field": field_name,
                "value": value,
                "min": limits["min"],
                "max": limits["max"]
            }
        )
    return True



def validate_year_value(year: int, value: float, max_value: float) -> bool:
    """Validates values for specific years"""
    return 0 <= year and 0 <= value <= max_value