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


#dynamic model 
from typing import Any,Dict,Type,List
from datetime import date 
from pydantic import create_model

Category_data = {
    1:{'name':'Food','fields':{'expiry':(date,...),'ingredients':(List[str],...)}},
    2:{'name':'Games','fields':{'genre':(List[str],...),'rating':(float,Field(gt=0.0, le=5.0))}},
    3:{'name':'Electronics','fields':{'specific':(List[str],...)}}
}

def use_model(id:int)->Type[BaseModel]:
    cat = Category_data.get(id)
    if not cat:
        raise HTTPException(status_code=404,detail=f"Product category {id} not found")
    base_data = {
        'sku':(str,...),
        'price':(float,Field(...,gt=0))
    }
    all_data = {**base_data,**cat['fields']}
    cat_name= cat['name']
    ProductModel= create_model(
        f'Dynamic{cat_name}Model',
        **all_data
    )
    return ProductModel

@app.post("/products/ecom/{id}")
async def creat_dynamic_model(
    id:int,
    request_body:Dict[str,Any]
):
    Model = use_model(id)
    try:
        valid_product = Model(**request_body)
    except Exception as error:
        raise HTTPException(status_code=422,detail = str(error))
    return{
        'message':"product created",
        'product': valid_product.model_dump()
        }

data_for_get = {

    # =========================
    # FOOD
    # categorical_id = 1
    # =========================

    101: {
        'categorical_id': 1,
        'sku': 'dosa',
        'price': 200.1,
        'attributes': {
            'expiry': '2026-11-23',
            'ingredients': ['batter', 'potato', 'onion']
        }
    },

    102: {
        'categorical_id': 1,
        'sku': 'idli',
        'price': 120.0,
        'attributes': {
            'expiry': '2026-10-15',
            'ingredients': ['rice', 'urad dal', 'salt']
        }
    },

    103: {
        'categorical_id': 1,
        'sku': 'biryani',
        'price': 350.5,
        'attributes': {
            'expiry': '2026-09-10',
            'ingredients': ['rice', 'chicken', 'onion', 'spices']
        }
    },


    # =========================
    # GAMES
    # categorical_id = 2
    # =========================

    201: {
        'categorical_id': 2,
        'sku': 'gta6',
        'price': 4999.0,
        'attributes': {
            'genre': ['action', 'adventure', 'open-world'],
            'rating': 4.8
        }
    },

    202: {
        'categorical_id': 2,
        'sku': 'minecraft',
        'price': 1999.0,
        'attributes': {
            'genre': ['sandbox', 'survival', 'adventure'],
            'rating': 4.7
        }
    },

    203: {
        'categorical_id': 2,
        'sku': 'tekken8',
        'price': 2999.0,
        'attributes': {
            'genre': ['fighting', 'action'],
            'rating': 4.6
        }
    },


    # =========================
    # ELECTRONICS
    # categorical_id = 3
    # =========================

    301: {
        'categorical_id': 3,
        'sku': 'iphone17',
        'price': 79999.0,
        'attributes': {
            'specific': ['256GB', 'OLED', '5G']
        }
    },

    302: {
        'categorical_id': 3,
        'sku': 'samsung-tv',
        'price': 54999.0,
        'attributes': {
            'specific': ['55-inch', '4K', 'OLED', 'HDR']
        }
    },

    303: {
        'categorical_id': 3,
        'sku': 'gaming-laptop',
        'price': 89999.0,
        'attributes': {
            'specific': ['16GB RAM', '1TB SSD', 'RTX 4060']
        }
    }
}

@app.get("/product/getecom/{id}")
async def get_data(id:int):
    product = data_for_get[int(id)]
    if not product:
        raise HTTPException(status_code=404,detail= "product not exist")
    cat_id = product['categorical_id']
    ResponseModel = use_model(cat_id)
    response_data = {
        'sku':product['sku'],
        'price':product['price'],
        **product['attributes']
    }
    try:
        return ResponseModel(**response_data)
    except Exception as error:
        raise HTTPException(status_code=422,detail=str(error))

@app.get('/products/all',response_model=List[Dict[str,Any]])
async def get_all():
    return list(data_for_get.values())