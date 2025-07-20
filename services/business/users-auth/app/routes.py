from fastapi import APIRouter, Depends, HTTPException, Request, Security, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse

from app.services import get_access_token, get_refresh_token, refresh_token, validate_access_token, validate_refresh_token, create_user
from app.utils.contrib import reusable_oauth2
from app.schemas import JWTToken, JWTRefreshToken, JWTAccessToken, RefreshToken, CreateUser, UserCreated
from app import settings

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


@router.get("/.well-known/jwks.json", response_class=JSONResponse, include_in_schema=False)
async def jwks():
    return settings.JWKS


@router.post("/create-user", response_model=UserCreated, status_code=status.HTTP_201_CREATED)
async def create_user_request(
    request: Request,
    user_model: CreateUser
):
    kafka_client = request.app.state.kafka_client
    return await create_user(user_model=user_model, kafka_client=kafka_client)