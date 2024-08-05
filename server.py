from typing import List
from fastapi import FastAPI
import os
from getAllProductsLinks import scrape_product_links
from build_links_scraper import scrape_product_links_build
from pydantic import BaseModel
from get_shawfloor_products_details import get_shawfloor_products_data
from get_build_products_details import get_build_products_data
from get_buildersInterior_products_details import get_buildersInteriors_products_data
from buildersinteriors_links_scraper import scrape_product_links_buiders_interiors
from llflooring_links_scraper import scrape_product_links_llflooring
from get_llflooring_products_details import get_llflooring_products_data
app = FastAPI()
from fastapi.staticfiles import StaticFiles
base_directory = "products"
if not os.path.exists(base_directory):
    os.makedirs(base_directory)

app.mount("/products", StaticFiles(directory=base_directory), name="products")
class URLRequest(BaseModel):
    urls: List[str]

@app.post("/getcarpet")
async def get_products_details(request: URLRequest):
    product = get_shawfloor_products_data(request.urls)
    return product
class URLsRequest(BaseModel):
    no: int
    url:str

class URLsRequest(BaseModel):
    min: int
    max: int
    category:str

@app.post("/page-products-links")
async def get_products_links(request: URLsRequest):
    try:
        if request.category == "carpets":
            product_links = scrape_product_links(request.min, request.max, request.category[:-1])
        elif request.category == "hardwoods":
            product_links = scrape_product_links(request.min, request.max, request.category[:-1])
        elif request.category == "vinyls":
            product_links = scrape_product_links(request.min, request.max, request.category[:-1])
        elif request.category == "tiles":
            product_links = await scrape_product_links_build("https://www.build.com/shop-all-vanities/c113572?page=", request.min, request.max)
        elif request.category == "sinks":
            product_links = await scrape_product_links_build("https://www.build.com/undermount-kitchen-sinks/c113813?page=", request.min, request.max)
        elif request.category == "faucets":
            product_links = await scrape_product_links_build("https://www.build.com/all-kitchen-faucets/c108514?page=", request.min, request.max)
        elif request.category == "vanities":
            product_links = await scrape_product_links_build("https://www.build.com/shop-all-vanities/c113572?page=", request.min, request.max)
        elif request.category == "doors":
            product_links = await scrape_product_links_build("https://www.build.com/all-doors-main/c82041374?page=", request.min, request.max)
        elif request.category == "laminates":
            product_links = await scrape_product_links_llflooring('https://www.llflooring.com/c/laminate-flooring/', request.min, request.max)   
        elif request.category == "countertops":
            product_links = await scrape_product_links_buiders_interiors('https://www.buildersinteriors.com/shop/slab/?bi=1&really_curr_tax=49-product_cat',request.min, request.max) 
        unique_product_links = list(set(product_links))            
        return {"product_links": unique_product_links}
    except Exception as e:
        print(e)
        # raise HTTPException(status_code=500, detail=str(e)) 

class URLRequest(BaseModel):
    urls: List[str]
    category: str

@app.post("/fetch-products")
async def get_products_details(request: URLRequest):
    try:
        if request.category == "carpets":
            products_data = get_shawfloor_products_data(request.urls, request.category)
        elif request.category == "hardwoods":
            products_data = get_shawfloor_products_data(request.urls, request.category)
        elif request.category == "vinyls":
            products_data = get_shawfloor_products_data(request.urls, request.category)
        elif request.category == "tiles":
            products_data = get_build_products_data(request.urls, request.category)
        elif request.category == "sinks":
            products_data = get_build_products_data(request.urls, request.category)
        elif request.category == "faucets":
            products_data = get_build_products_data(request.urls, request.category)
        elif request.category == "vanities":
            products_data = get_build_products_data(request.urls, request.category)
        elif request.category == "doors":
            products_data = get_build_products_data(request.urls, request.category)
        elif request.category == "laminates":
            products_data = await get_llflooring_products_data(request.urls)   
        elif request.category == "countertops":
            products_data = get_buildersInteriors_products_data(request.urls)    
        return products_data
    except Exception as e:
        print(e)
        # raise HTTPException(status_code=500, detail=str(e)) 