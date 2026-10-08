import re
from fastapi import HTTPException, Request

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

def get_owner_email(request: Request) -> str:
    email = str(request.session.get("email") or "").strip().lower()
    if not EMAIL_PATTERN.fullmatch(email):
        raise HTTPException(status_code=401, detail="Authentication required.")
    return email
