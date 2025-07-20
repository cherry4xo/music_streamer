from typing import Optional
from tortoise import Model, fields
from tortoise.exceptions import DoesNotExist
from pydantic import UUID4
from app.schemas import CreateUser
from app.utils import password

class BaseModel(Model):
    uuid = fields.UUIDField(pk=True)
    async def to_dict(self):
        d = {}
        for field in self._meta.db_fields:
            d[field] = getattr(self, field)
        for field in self._meta.backward_fk_fields:
            d[field] = await getattr(self, field).all().values()
        return d

    class Meta:
        abstract = True


class User(BaseModel):
    username = fields.CharField(max_length=255, unique=True)
    email = fields.CharField(max_length=255, unique=True)
    password_hash = fields.CharField(max_length=255, null=True)
    roles = fields.TextField(default="user")
    
    @classmethod
    async def get_by_uuid(cls, uuid: UUID4) -> Optional["User"]:
        try:
            query = cls.get_or_none(uuid=uuid)
            model = await query
            return model
        except DoesNotExist:
            return None
        
    @classmethod
    async def get_by_username(cls, username: str) -> Optional["User"]:
        try:
            query = cls.get_or_none(username=username)
            model = await query
            return model
        except DoesNotExist:
            return None
        
    @classmethod
    async def get_by_email(cls, email: str) -> Optional["User"]:
        try:
            query = cls.get_or_none(email=email)
            model = await query
            return model
        except DoesNotExist:
            return None
        
    @classmethod
    async def create(cls, user: CreateUser) -> "User":
        user_dict = user.model_dump(exclude=["password"])
        password_hash = password.get_password_hash(password=user.password)
        model = cls(**user_dict, password_hash=password_hash)
        await model.save()
        return model
        
    def __str__(self) -> str:
        return self.username
    
    class Meta:
        table = "users"