
from fastapi import APIRouter

from app.api.endpoints import (
    auth, 
    user
)

app_routers = APIRouter()


app_routers.include_router(auth.router, prefix="/auth", tags=["/Auth"])
app_routers.include_router(user.router, prefix="/users", tags=["/Users"])