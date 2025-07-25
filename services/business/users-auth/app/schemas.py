from pydantic import BaseModel, UUID4


class CredentialsSchema(BaseModel):
    email: str | None
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
    sub: UUID4 = None
    token_type: str = None


class RefreshToken(BaseModel):
    refresh_token: str


class CreateUser(BaseModel):
    username: str
    email: str
    password: str


class UserCreated(BaseModel):
    uuid: UUID4
    username: str
    email: str


class Msg(BaseModel):
    msg: str