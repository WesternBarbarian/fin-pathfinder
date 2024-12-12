from typing import Dict, Optional, List
from database.database import database  # Updated import
from database.models import Scenario

async def save_scenario(scenario_name: str, user_data: Dict) -> bool:
    """Save the current user data as a scenario"""
    try:
        query = Scenario.__table__.insert().values(
            name=scenario_name,
            user_data=user_data
        )
        await database.execute(query)
        return True
    except Exception:
        return False

async def get_scenario(scenario_name: str) -> Optional[Dict]:
    """Retrieve a specific scenario by name"""
    query = Scenario.__table__.select().where(Scenario.name == scenario_name)
    result = await database.fetch_one(query)
    if result:
        return dict(result['user_data'])
    return None

async def get_all_scenarios() -> List[str]:
    """Retrieve all scenario names"""
    query = Scenario.__table__.select()
    results = await database.fetch_all(query)
    return [result['name'] for result in results]