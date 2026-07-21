


from fastapi import FastAPI 
from contextlib import asynccontextmanager 

from app.core.logger import get_logger
from app.db.session import check_db_connection


logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app : FastAPI) : 
    logger.info("app starting ... ") 

    is_ok = await check_db_connection()
    if not is_ok : 
        logger.error("Database is not ok")
    
    else : 
        logger.info("Database is ok")
        

    yield


app = FastAPI(
    lifespan=lifespan
) 


@app.get("/")
async def main() : 
    return {"Detail" : "welcome"}


