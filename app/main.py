


from fastapi import FastAPI 
from contextlib import asynccontextmanager 

from app.core.logger import get_logger , configure_logging 
from app.db.session import check_db_connection , async_engine 

from app.db.redis import get_redis , close_redis


logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app : FastAPI) : 
    logger.info("app starting ... ") 

    is_ok = await check_db_connection()

    configure_logging()
    
    if not is_ok : 
        logger.error("Database is not ok")
    
    else : 
        logger.info("Database is ok")

    try : 
        await get_redis().ping() 
        logger.info("Redis is connected!")

    except Exception as exc : 
        logger.info(f"Redis is not ok : {exc}")


    yield

    logger.info("Shutting down ... ")

    await async_engine.dispose() 
    await close_redis() 

    logger.info("Goodbuy")


app = FastAPI(
    lifespan=lifespan
) 


@app.get("/")
async def main() : 
    return {"Detail" : "welcome"}


