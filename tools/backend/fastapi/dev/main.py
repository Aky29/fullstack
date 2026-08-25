from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class iteams(BaseModel):
    name:str
    id:int
    price:float
    tax:Optional[float]=None

@app.get("/items/{name}")
async def items(name:str, price:int|None =None):
    return {"item name":name , "price":price}

@app.get("/item")
async def many_items():
    items_list = {"name":"itm1","price":100.2,"id":12331,"tax":10.2}
    return iteams(**items_list)