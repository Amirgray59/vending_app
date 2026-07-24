
from fastapi import APIRouter

from app.api.endpoints import (
    auth
)

app_routers = APIRouter()


app_routers.include_router(auth.router, prefix="/auth")
