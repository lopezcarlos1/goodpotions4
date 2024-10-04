from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_bottles(potions_delivered: list[PotionInventory], order_id: int):
    """ """
    potion_amount = 0
    ml_used = 0
    for potions in potions_delivered:
        if potions.potion_type == [0, 100, 0, 0]:
            ml_used = (potions.quantity*potions.potion_type[1]) + ml_used
            potion_amount = potions.quantity + potion_amount

    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_potions = num_green_potions - %d" % (potion_amount)))
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET  num_green_ml = num_green_ml - %d" % (ml_used)))

    print(f"potions delievered: {potions_delivered} order_id: {order_id}")

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.

    with db.engine.begin() as connection:
        ml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory")).scalar()
        if ml < 100:
            return []
    
    greenpotion = ml // 100
    return [
            {
                "potion_type": [0, 100, 0, 0],
                "quantity": greenpotion,
            }
        ]

if __name__ == "__main__":
    print(get_bottle_plan())
