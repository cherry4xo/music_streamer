from enum import Enum
from typing import Optional, Any
import logging

from pydantic import UUID4
from tortoise import Model, fields
from tortoise.exceptions import DoesNotExist, IntegrityError
from tortoise.contrib.pydantic import pydantic_model_creator


logger = logging.getLogger(__name__)


class UserStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class ThemePreference(str, Enum):
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"


class LanguagePreference(str, Enum):
    EN = "en"
    ES = "es"


class ProfileVisibility(str, Enum):
    PUBLIC = "public"       # Everyone can see the profile (if public profiles exist)
    PRIVATE = "private"     # Only the user can see (or maybe staff)


class ActionActorType(str, Enum):
    USER = "user"
    ADMIN = "admin"
    SYSTEM = "system"


class AccountActivityType(str, Enum):
    EMAIL_UPDATED = "email_updated"
    USERNAME_UPDATED = "username_updated"
    PROFILE_UPDATED = "profile_updated"
    STATUS_CHANGED = "status_changed"
    PASSWORD_RESET_REQUESTED = "password_reset_requested" # Request logged here
    ACCOUNT_CREATED = "account_created"
    ACCOUNT_DELETED = "account_deleted" # Soft deletion event
    ACCOUNT_SUSPENDED = "account_suspended"
    ACCOUNT_REACTIVATED = "account_reactivated"


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
    username = fields.CharField(max_length=100, unique=True)
    email = fields.CharField(max_length=255, unique=True)
    recovery_email = fields.CharField(max_length=255, null=True)

    first_name = fields.CharField(max_length=100, null=True)
    second_name = fields.CharField(max_length=100, null=True)
    display_name = fields.CharField(max_length=100, null=True)
    status = fields.CharEnumField(UserStatus, default=UserStatus.PENDING, index=True)

    is_email_verified = fields.BooleanField(default=False)
    last_login = fields.DatetimeField(auto_now_add=True)
    theme_preference = fields.CharEnumField(ThemePreference, default=ThemePreference.SYSTEM, index=True)
    language_preference = fields.CharEnumField(LanguagePreference, default=LanguagePreference.EN, index=True)

    email_notifications_enabled = fields.BooleanField(default=True)
    email_marketing_notifications_enabled = fields.BooleanField(default=True)
    push_notifications_enabled = fields.BooleanField(default=True)

    profile_visibility = fields.CharEnumField(ProfileVisibility, default=ProfileVisibility.PUBLIC, index=True)
    activity_sharing_enabled = fields.BooleanField(default=True, index=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    edited_at = fields.DatetimeField(auto_now=True)

    activity_log: fields.ReverseRelation["AccountActivityLog"]

    async def change_username(self, new_username: str) -> None:
        if self.username == new_username:
            logger.warning(f"User {self.id} tried to change username to {new_username} but it is the same as the current one")
            return
        
        existing_user_with_same_username = await User.get_or_none(
            username=new_username,
            id__not=self.id 
        )
        if existing_user_with_same_username:
            logger.warning(f"User {self.id} tried to change username to {new_username} but it is already taken")
            return
        
        self.username = new_username
        try:
            await self.save()
        except IntegrityError as e:
            logger.error(f"Error changing username for user {self.id}: {e}")

    async def get_by_fields(self, **kwargs) -> Optional["User"]:
        try:
            query = User.get_or_none(**kwargs)
            model = await query
            return model
        except DoesNotExist:
            return None

    @classmethod
    async def get_by_email(self, email: str) -> Optional["User"]:
        return User.get_by_fields(email=email)
        
    @classmethod
    async def get_by_username(self, username: str) -> Optional["User"]:
        return User.get_by_fields(username=username)
    
    @classmethod
    async def get_by_uuid(self, uuid: UUID4) -> Optional["User"]:
        return User.get_by_fields(uuid=uuid)

    @classmethod
    async def change_email(self, new_email: str) -> None:
        if self.email == new_email:
            logger.warning(f"User {self.id} tried to change email to {new_email} but it is the same as the current one")
            return
        
        existing_user_with_same_email = await User.get_or_none(
            email=new_email,
            id__not=self.id 
        )
        if existing_user_with_same_email:
            logger.warning(f"User {self.id} tried to change email to {new_email} but it is already taken")
            return
        
        self.email = new_email
        try:
            await self.save()
        except IntegrityError as e:
            logger.error(f"Error changing email for user {self.id}: {e}")


    class Meta:
        table = "users"
        ordering = ["created_at"]


class AccountActivityLog(BaseModel):
    user: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField("models.User", related_name="activity_log")
    activity_type = fields.CharEnumField(AccountActivityType, index=True)
    detail = fields.JSONField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    actor_id = fields.UUIDField(null=True)
    actor_type = fields.CharEnumField(ActionActorType, null=True)

    def __str__(self):
        return f"{self.activity_type} for {self.user.id} at {self.created_at}"

    class Meta:
        table = "account_activity_log"
        ordering = ["-created_at"]