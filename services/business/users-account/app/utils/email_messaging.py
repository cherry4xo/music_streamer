from typing import Optional
from datetime import datetime

from smtplib import SMTP_SSL as SMTP
from email.mime.text import MIMEText
from random import random

from fastapi.exceptions import HTTPException
from pydantic import UUID4

from app.models import User
from 