from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter()

@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    catalog=[]
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory")).scalar()

        if result > 0:
            catalog.append({
                "sku": "GREEN_POTION_0",
                "name": "green potion",
                "quantity": result,
                "price": 50,
                "potion_type": [0, 100, 0, 0], #only return 6 catalog items
            })
    return catalog
