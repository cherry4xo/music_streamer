from enum import Enum
from typing import Optional
from tortoise import Model, fields
from tortoise.exceptions import DoesNotExist
from tortoise.contrib.pydantic import pydantic_model_creator


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

    first_name = fields.CharField(max_length=100)
    second_name = fields.CharField(max_length=100, null=True)
    display_name = fields.CharField(max_length=100)
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


User_Pydantic = pydantic_model_creator(User, name="User")
UserIn_Pydantic = pydantic_model_creator(User, name="UserIn", exclude_readonly=True,
    exclude=(
        "status", "is_email_verified", "last_login",
        "email_notifications_enabled", "email_marketing_notifications_enabled",
        "push_notifications_enabled", "profile_visibility",
        "activity_sharing_enabled",
        "display_name", "recovery_email"
    )
)
UserUpdate_Pydantic = pydantic_model_creator(
    User, name="UserUpdate", exclude_readonly=True, optional="__all__",
    exclude=("email", "username", "status", "is_email_verified", "last_login")
)

AccountActivityLog_Pydantic = pydantic_model_creator(AccountActivityLog, name="AccountActivityLog")