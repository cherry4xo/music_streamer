from datetime import datetime
import logging

from fastapi import HTTPException, status
from pydantic import UUID4

from app.models import User
from app.schemas import UserIn_Pydantic, UserGet_Pydantic, UserChangeUsername
from app.logger import log_calls
from app.utils.email_messaging import send_confirm_email, EmailTopic
from app.redis import RedisInterface

logger = logging.getLogger(__name__)

@log_calls
async def get_user_me(user_id: UUID4):
    user = await User.get_or_none(uuid=user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User account not found"
        )
    
    return user


@log_calls
async def change_username(user_id: UUID4, username: UserChangeUsername):
    user = await User.get_or_none(uuid=user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User account not found"
        )
    
    await user.change_username(new_username=username.username)


@log_calls
async def send_email_confirmation_letter(user_id: UUID4):
    user = await User.get_by_uuid(uuid=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User account not found"
        )
    
    if user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified"
        )
    
    await send_confirm_email(user=user)


@log_calls
async def confirm_email(user_id: UUID4, code: str):
    user = await User.get_by_uuid(uuid=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User account not found"
        )
    
    if user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified"
        )
    
    key = "generated_code"
    
    record = await RedisInterface.get_record(type=EmailTopic.CONFIRM_EMAIL.value, id=user.uuid, key=key)
    if record is not None:
        code_in_db = record.get(key, None)
        if code_in_db is not None:
            code_in_db = code_in_db.decode("utf-8")
            if code_in_db == code:
                user.is_email_verified = True
                await user.save()
                return
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect confirmation code",
            )
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Confirmation code has been expired"
        )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Confirmation code has not set",
    )
        
        
