from datetime import timedelta

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas import CreateUser, JWTAccessToken, JWTRefreshToken, JWTToken, CredentialsSchema, RefreshToken, UserCreated
from app.models import User
from app.utils.contrib import authenticate, validate_refresh_token, reusable_oauth2, refresh_oauth2, get_current_user
from app.utils.jwt import create_access_token, create_refresh_token
from app import settings
from app.logger import log_calls
from app import metrics
from app.kafka_interface import KafkaInterface


@log_calls
async def get_access_token(credentials: OAuth2PasswordRequestForm = Depends()):
    credentials = CredentialsSchema(email=credentials.username, password=credentials.password)
    user = await authenticate(credentials=credentials)

    if not user:
        metrics.auth_logins_total.labels(status="failure").inc()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

    user_roles = user.roles

    token_data = {
        "user_uuid": str(user.uuid),
        "roles": user_roles,
    }

    access_token = create_access_token(data=token_data, expires_delta=access_token_expires)
    refresh_token = create_refresh_token(data=token_data, expires_delta=refresh_token_expires)

    metrics.auth_logins_total.labels(status="success").inc()

    return JWTToken(refresh_token=refresh_token, access_token=access_token, token_type="bearer")


@log_calls
async def get_refresh_token(credentials: OAuth2PasswordRequestForm = Depends()):
    credentials = CredentialsSchema(email=credentials.username, password=credentials.password)
    user = await authenticate(credentials=credentials)

    if not user:
        metrics.auth_refresh_token_logins_total.labels(status="failure").inc()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )
    
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

    refresh_token = create_refresh_token(data={"user_uuid": str(user.uuid)}, expires_delta=refresh_token_expires)

    metrics.auth_refresh_token_logins_total.labels(status="success").inc()

    return JWTRefreshToken(refresh_token=refresh_token, token_type="bearer")


@log_calls
async def refresh_token(token: RefreshToken):
    access_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    user = await validate_refresh_token(token=token.refresh_token)

    if user is None:
        metrics.auth_token_refreshes_total.labels(status="failure").inc()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The user with uuid in token does not exist"
        )
    
    new_access_token = create_access_token(data={"user_uuid": str(user.uuid)}, expires_delta=access_token_expires)

    metrics.auth_token_refreshes_total.labels(status="success").inc()

    return JWTAccessToken(access_token=new_access_token, token_type="bearer")


@log_calls
async def validate_access_token(token: str = Depends(reusable_oauth2)):
    try:
        user = await get_current_user(token=token)
        metrics.auth_token_validations_total.labels(status="success").inc()
        return user
    except HTTPException as e:
        metrics.auth_token_validations_total.labels(status="failure").inc()
        raise e
    

@log_calls
async def create_user(user_model: CreateUser, kafka_client: KafkaInterface):
    try:
        user_db = await User.get_by_email(email=user_model.email)

        if user_db is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already exists")
        
        user_db = await User.get_by_username(username=user_model.username)

        if user_db is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this username already exists")
        
        user_db = await User.create(user=user_model)

        metrics.auth_user_registrations_total.labels(status="success").inc()

        user_created_event = {
            "event_type": "user_created",
            "uuid": str(user_db.uuid),
            "email": user_db.email,
            "username": user_db.username,
        }

        produce_topic = settings.KAFKA_PRODUCE_TOPICS[0]

        await kafka_client.send_event(produce_topic, user_created_event)

        return UserCreated(uuid=user_db.uuid, email=user_db.email, username=user_db.username)
    except Exception as e:
        metrics.auth_user_registrations_total.labels(status="failure").inc()
        raise e