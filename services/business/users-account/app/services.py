from datetime import datetime

from fastapi import HTTPException, status
from pydantic import UUID4

from app.models import User
from app.schemas import UserIn_Pydantic, UserGet_Pydantic
from app.logger import log_calls


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
async def change_username(user_id: UUID4, username: str):
    user = await User.get_or_none(uuid=user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User account not found"
        )
    
    await user.change_username(new_username=username)


