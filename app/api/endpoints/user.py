"""User management endpoints."""
from math import ceil
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import CurrentUser, DBSession, require_permission
from app.schema.common import Page, PageMeta
from app.schema.user import (
    UserChangePassword,
    UserCreate,
    UserRead,
    UserUpdate,
)
from app.services.user_service import UserService

router = APIRouter()


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="add new user ",
    dependencies=[Depends(require_permission("user.create"))],
)
async def create_user(payload: UserCreate, db: DBSession) -> UserRead:
    service = UserService(db)
    user = await service.create_user(payload)
    return UserRead.model_validate(user)


@router.get(
    "",
    response_model=Page[UserRead],
    summary="user list",
    dependencies=[Depends(require_permission("user.view"))],
)
async def list_users(
    db: DBSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> Page[UserRead]:
    service = UserService(db)
    users, total = await service.list_users(
        offset=(page - 1) * page_size, limit=page_size
    )
    return Page[UserRead](
        items=[UserRead.model_validate(u) for u in users],
        meta=PageMeta(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=max(1, ceil(total / page_size)),
        ),
    )


@router.get(
    "/{user_id}",
    response_model=UserRead,
    summary="user detail",
    dependencies=[Depends(require_permission("user.view"))],
)
async def get_user(user_id: UUID, db: DBSession) -> UserRead:
    service = UserService(db)
    user = await service.get_user(user_id)
    return UserRead.model_validate(user)


@router.patch(
    "/{user_id}",
    response_model=UserRead,
    summary="edit user",
    dependencies=[Depends(require_permission("user.update"))],
)
async def update_user(
    user_id: UUID, payload: UserUpdate, db: DBSession
) -> UserRead:
    service = UserService(db)
    user = await service.update_user(user_id, payload)
    return UserRead.model_validate(user)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="soft delete user",
    dependencies=[Depends(require_permission("user.delete"))],
)
async def delete_user(user_id: UUID, db: DBSession) -> None:
    service = UserService(db)
    await service.delete_user(user_id)


@router.post(
    "/me/change-password",
    status_code=status.HTTP_200_OK,
    summary="change current user",
)
async def change_password(
    payload: UserChangePassword,
    current: CurrentUser,
    db: DBSession,
) -> dict:
    service = UserService(db)
    await service.change_password(current, payload.old_password, payload.new_password)
    return {"success": True, "message": "your password has been changed."}
