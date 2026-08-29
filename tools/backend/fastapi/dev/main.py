from fastapi import FastAPI,Body
from pydantic import BaseModel,validate_call,ValidationError,StringConstraints
from typing import Optional,Annotated
from pydantic import Field
app = FastAPI()

class iteams(BaseModel):
    name:str = Body(...)
    id:int = Body 
    price:float
    tax:Optional[float]=None

#path parameter
@app.get("/items/{name}")
async def items(name:str, price:int|None =None,id:int|None= None,expiry:int|None=None):
    return {"item name":name , "price":price,"id":id,"expiry":expiry}

@app.get("/item")
async def many_items():
    items_list = {"name":"itm1","price":100.2,"id":12331,"tax":10.2}
    return iteams(**items_list)

#data validation 
class Item(BaseModel):
    name:str = Field(...,min_length=4)
    description:str
    price:float

@validate_call
def validate_name(name:Annotated[str,StringConstraints(min_length=4)]):
    return name 
try:
    name = validate_name(name = 'janu')
    product = Item(name="comb",description = "used to fix hair",price= 400.1)
    print(product)
    print(product.model_dump(exclude = ("description")))
    print("name is valid")
except ValidationError as error:
    print(f"error occured {error}")

@app.post("/product")
async def create_item(item:Item):
    return item 

#pydantic basemodel with fastapi body 

class user(BaseModel):
    name:str = Body(...)
    id:str = Body(...)
    caste:Annotated[str,Body()]

#additional validation 
from fastapi import Query

@app.get('/person')
async def human(id:Annotated[str|None , Query(max_length=10)]):
    df = {}
    return df[id]

#data injection
from fastapi import Depends,Header,Path,HTTPException,status

async def get_db_session():
    session = {1 : user(name ="anish",id = '601823542',caste='obc')}
    yield session

DBsession = Annotated[dict,Depends(get_db_session)]
async def get__user(token:Annotated[str|None , Header()]):
    user = {'username' : "test_user"}
    return user

CurrentUser = Annotated[dict,Depends(get__user)]

@app.get("/productid/{product_id}")
async def read_items(product_id:Annotated[int,Path(ge=1)],db : DBsession):
    if product_id not in db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = "Item not present")
    return {'id':product_id,**db[product_id].model_dump()}
