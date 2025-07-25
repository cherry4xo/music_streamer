from datetime import datetime, timedelta

import jwt
from fastapi.encoders import jsonable_encoder

from app import settings

ALGORITHM = "RS256"
access_token_jwt_subject = "access"
refresh_token_jwt_subject = "refresh"

JWT_ISSUER = "users-auth"
JWT_AUDIENCE = "api-gateway"


def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({
        "exp": expire.timestamp(), 
        "iss": JWT_ISSUER,
        "aud": [JWT_AUDIENCE]
    })
    encoded_jwt = jwt.encode(
        payload=to_encode, 
        key=settings.JWT_PRIVATE_KEY,
        algorithm=ALGORITHM,
        headers={"kid": settings.KEY_ID}
    )
    return encoded_jwt


def create_refresh_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({
        "exp": expire.timestamp(),
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "token_type": "refresh"
    })
    encoded_jwt = jwt.encode(
        payload=to_encode, 
        key=settings.JWT_PRIVATE_KEY,
        algorithm=ALGORITHM,
        headers={"kid": settings.KEY_ID}
    )

    return encoded_jwt