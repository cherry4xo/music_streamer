from enum import Enum
from typing import Optional
from datetime import datetime

from smtplib import SMTP_SSL as SMTP
from smtplib import SMTPException
from email.mime.text import MIMEText
from random import randint

from fastapi.exceptions import HTTPException
from pydantic import UUID4

from app.models import User
from app.redis import RedisInterface
from app import settings


class EmailTopic(Enum):
    CONFIRM_EMAIL = "email-confirm"
    CHANGE_EMAIL = "change-email"


async def send_email_letter(to: str, subject: str, main_text: str):
    try:
        msg = MIMEText(main_text)
        msg["Subject"] = subject
        msg["From"] = settings.EMAIL
        msg["to"] = to

        with SMTP(host=settings.SMTP_HOST, port=settings.SMTP_PORT) as smtp:
            smtp.set_debuglevel(False)
            smtp.login(settings.SMTP_LOGIN, settings.SMTP_PASSWORD)
            try:
                smtp.sendmail(settings.EMAIL, to, msg.as_string())
            except SMTPException as e:
                raise HTTPException(status_code=500, detail=f"Something went wrong with email sending: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Something went wrong with email sending: {str(e)}")
    

async def send_confirm_email(user: User):
    topic = EmailTopic.CONFIRM_EMAIL
    generated_code = "".join([str(randint(0, 9)) for _ in range(6)])
    await send_email_letter(user.email, "Confirm your email", f"Your confirmation code: {generated_code}")
    store_mapping = { "generated_code": generated_code }
    await RedisInterface.create_record(type=topic.value, 
                                       id=str(user.uuid), 
                                       data=store_mapping, 
                                       expire=settings.EMAIL_CONFIRMATION_LETTER_EXPIRE_SECONDS)
    