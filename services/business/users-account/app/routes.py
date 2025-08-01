import logging
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Header, status
from pydantic import UUID4

from app.models import User
from app.schemas import UserConfirmEmail, UserGet_Pydantic, UserChangeUsername
from app import services


router = APIRouter()

logger = logging.getLogger(__name__)


async def get_user_id_from_gateway(x_user_id: Annotated[str | None, Header(alias="X-User-Id")] = None) -> str:
    """
    Dependency to extract the User ID passed by the API Gateway (Krakend).
    Raises an exception if the header is missing, implying a configuration error
    or unauthorized access attempt bypassing the gateway.
    """
    logger.info(f"Getting user {x_user_id}")
    if x_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User identifier missing in request from gateway.",
        )
    return x_user_id


@router.get("/me", response_model=UserGet_Pydantic, status_code=status.HTTP_200_OK)
async def route_me(
    user_id: UUID4 = Depends(get_user_id_from_gateway)
):
    return await services.get_user_me(user_id=user_id)


@router.post("/me/username", status_code=status.HTTP_200_OK)
async def route_change_username(
    username: UserChangeUsername,
    user_id: UUID4 = Depends(get_user_id_from_gateway)
):
    return await services.change_username(user_id=user_id, username=username)


@router.post("/me/email/send_confirm_code", status_code=status.HTTP_200_OK)
async def route_send_email_confirm_code(
    user_id: UUID4 = Depends(get_user_id_from_gateway)
):
    return await services.send_email_confirmation_letter(user_id=user_id)


@router.post("/me/email/confirm_email", status_code=status.HTTP_200_OK)
async def route_confirm_email(
    body: UserConfirmEmail,
    user_id: UUID4 = Depends(get_user_id_from_gateway)
):
    return await services.confirm_email(user_id=user_id, code=body.code)