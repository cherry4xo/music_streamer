from pydantic import BaseModel, UUID4


class CredantialsSchema(BaseModel):
    username: str | None
    password: str

    class Config: 
        json_schema_extra = {"example": {"email": "john.doe@example.com", "password": "secret"}}


class JWTToken(BaseModel):
    refresh_token: str
    access_token: str
    token_type: str = "bearer"


class JWTAccessToken(BaseModel):
    access_token: str
    token_type: str = "bearer"


class JWTRefreshToken(BaseModel):
    refresh_token: str
    token_type: str = "bearer"


class JWTTokenPayload(BaseModel):
    user_uuid: UUID4 = None
    token_kind: str = None


class RefreshToken(BaseModel):
    refresh_token: str


class Msg(BaseModel):
    msg: str