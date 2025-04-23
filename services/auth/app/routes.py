from fastapi import APIRouter, Depends, Security, status
from fastapi.security import OAuth2PasswordRequestForm

from app.servises import get_access_token, get_refresh_token, refresh_token, validate_access_token, validate_refresh_token
from app.utils.contrib import reusable_oauth2
from app.schemas import JWTToken, JWTRefreshToken, JWTAccessToken, RefreshToken

router = APIRouter()


@router.post("/access-token", response_model=JWTToken, status_code=status.HTTP_200_OK)
async def route_access_token(credentials: OAuth2PasswordRequestForm = Depends()):
    return await get_access_token(credentials=credentials)


@router.post("/refresh-token", response_model=JWTRefreshToken, status_code=status.HTTP_200_OK)
async def route_refresh_token(credentials: OAuth2PasswordRequestForm = Depends()):
    return await get_refresh_token(credentials=credentials)


@router.post("/refresh", response_model=JWTAccessToken, status_code=status.HTTP_200_OK)
async def route_refresh(token: RefreshToken):
    return await refresh_token(token=token)


@router.get("/validate", status_code=status.HTTP_200_OK)
async def route_validate(token: str = Security(reusable_oauth2)):
    return await validate_access_token(token=token)