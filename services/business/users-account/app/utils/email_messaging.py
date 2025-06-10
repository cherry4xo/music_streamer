from enum import Enum
from typing import Optional
from datetime import datetime

from smtplib import SMTP_SSL as SMTP
from smtplib import SMTPException
from email.mime.text import MIMEText
from random import random

from fastapi.exceptions import HTTPException
from pydantic import UUID4

from app.models import User
from app.redis import RedisInterface
from app import settings


class EmailTopic(Enum):
    CONFIRM = "email-confirm"


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
                raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))