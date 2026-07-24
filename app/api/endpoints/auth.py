"""
Auth endpoints — /login, /refresh, /logout, /me.
"""

from fastapi import APIRouter, Request, status

from app.api.deps import CurrentUser, DBSession, get_client_ip, get_user_agent
from app.schema.auth import LoginRequest, LogoutRequest, RefreshRequest, TokenPair
from app.schema.user import UserMe
from app.services.auth import AuthService

router = APIRouter()


@router.post(
    "/login",
    response_model=TokenPair,
    status_code=status.HTTP_200_OK,
    summary="enter user",
    description="enter with username / phone / email +   (access + refresh) .",
)
async def login(
    payload: LoginRequest,
    request: Request,
    db: DBSession,
) -> TokenPair:
    service = AuthService(db)
    _, tokens = await service.login(
        identifier=payload.identifier,
        password=payload.password,
        user_agent=get_user_agent(request),
        ip_address=get_client_ip(request),
    )
    return tokens


@router.post(
    "/refresh",
    response_model=TokenPair,
    summary="refresh token",
    description="send refresh token، gives new tokens (rotation).",
)
async def refresh_token(payload: RefreshRequest, db: DBSession) -> TokenPair:
    service = AuthService(db)
    return await service.refresh(payload.refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="logout",
    description="expire refresh token devices.",
)
async def logout(
    payload: LogoutRequest,
    current: CurrentUser,
    db: DBSession,
) -> dict:
    service = AuthService(db)
    count = await service.logout(
        user_id=current.id,
        refresh_token=payload.refresh_token,
        all_devices=payload.all_devices,
    )
    return {"success": True, "revoked_tokens": count}


@router.get(
    "/me",
    response_model=UserMe,
    summary="user info",
)
async def me(current: CurrentUser, db: DBSession) -> UserMe:
    # if superuser، returns all permissions  
    if current.is_superuser:
        from app.repositories.role_repository import PermissionRepository

        all_perms = await PermissionRepository(db).list_all()
        perm_codes = sorted(p.code for p in all_perms)
    else:
        perm_codes = sorted(current.permission_codes)

    return UserMe(
        id=current.id,
        username=current.username,
        email=current.email,
        phone=current.phone,
        full_name=current.full_name,
        status=current.status,
        is_superuser=current.is_superuser,
        last_login_at=current.last_login_at,
        created_at=current.created_at,
        updated_at=current.updated_at,
        roles=[r for r in current.roles],  # type: ignore[misc]
        permissions=perm_codes,
    )
