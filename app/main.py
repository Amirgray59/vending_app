


from fastapi import FastAPI 
from contextlib import asynccontextmanager 

app = FastAPI() 


@app.get("/")
async def main() : 
    return {"Detail" : "welcome"}


@asynccontextmanager
async def lifespan(app : FastAPI) : 
    yield