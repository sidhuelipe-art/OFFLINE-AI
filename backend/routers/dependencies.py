import re

from fastapi import Header, HTTPException


EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def get_owner_email(x_user_email: str | None = Header(default=None)) -> str:
    email = (x_user_email or "").strip().lower()
    if not EMAIL_PATTERN.fullmatch(email):
        raise HTTPException(status_code=401, detail="A valid X-User-Email header is required.")
    return email
