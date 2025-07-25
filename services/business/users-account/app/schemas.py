from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import BaseModel

from app.models import User, AccountActivityLog

class UserChangeUsername(BaseModel):
    username: str

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
UserGet_Pydantic = pydantic_model_creator(
    User, name="UserGet", exclude_readonly=True
)

AccountActivityLog_Pydantic = pydantic_model_creator(AccountActivityLog, name="AccountActivityLog")