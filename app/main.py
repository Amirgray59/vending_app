


from fastapi import FastAPI , Request, Response
from contextlib import asynccontextmanager 

from app.core.logger import get_logger , configure_logging 
from app.db.session import check_db_connection , async_engine 

from app.db.redis import get_redis , close_redis
from app.core.exceptions import AppException as AppExceptions
from fastapi.responses import ORJSONResponse 

from app.api.router import app_routers 


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

@app.exception_handler(AppExceptions)
async def app_exception_handler(request: Request, exc: AppExceptions) -> ORJSONResponse:
    logger.warning(
        "app_exception",
        path=request.url.path,
        error_code=exc.error_code,
        message=exc.message,
    )
    return ORJSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
            },
        },
    )



@app.get("/")
async def main() : 
    return {"Detail" : "welcome"}


app.include_router(app_routers)