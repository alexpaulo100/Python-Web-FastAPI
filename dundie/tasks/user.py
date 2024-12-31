import smtplib
from datetime import timedelta
from time import sleep

from sqlmodel import Session, select

from dundie.auth import create_access_token
from dundie.config import settings
from dundie.db import engine
from dundie.models.user import User


def send_email(email: str, message: str):
    if settings.emal.debug_mode is True:
        _send_email_debug(email, message)
    else:
        _send_email_smtp(email, message)


def _send_email_debug(email: str, message: str):
    """Mock email sending by printing to a file"""
    with open("email.log", "a") as f:
        sleep(3)
        f.write(f"---START EMAIL {email} ---\n" f"{message}\n" "---END OF EMAIL ---\n")


def _send_email_smtp(email: str, message: str):
    """Connect to SMTP server and send email"""
    with smtplib.SMTP_SSL(
        settings.email.smtp.server, settings.email.smtp_port
    ) as server:
        server.login(settings.email.smtp_user, settings.email.smtp_password)
        server.sendmail(
            settings.email.smtp_sender,
            email,
            message.encode("utf8"),
        )


MESSAGE = """\
From: Dundie <{sender}>
To : {to}
Subject: Password reset for Dundie

Please use the following link to reset your password:
"""
