from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    """ """
    total_cost = 0
    green_ml = 0



    for barrel in barrels_delivered:
        total_cost = total_cost + (barrel.price * barrel.quantity)
        green_ml = green_ml + (barrel.ml_per_barrel * barrel.quantity)

    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = gold - %d" % (total_cost)))
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET  num_green_ml = num_green_ml + %d" % (green_ml)))
    

    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    return "OK"

# Gets called once a day
@router.post("/plan") #securely allow o share between two
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)
    gold = 0

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory")).scalar()
        gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory")).scalar()
        if result > 10:
            return []
    
    plan = []
    for barrel in wholesale_catalog:
        if barrel.sku == "SMALL_GREEN_BARREL" and gold >= barrel.price:
            amount = gold // barrel.price
            if  amount > barrel.quantity:
                amount = barrel.quantity
            plan.append({ "sku": "SMALL_GREEN_BARREL","quantity": amount})
            break
        
    return plan

