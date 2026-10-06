from hashlib import pbkdf2_hmac
from hmac import compare_digest
from secrets import token_hex

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from database import get_db
import models

router = APIRouter(prefix="/auth", tags=["Authentication"])


class AuthRequest(BaseModel):
    email: EmailStr
    password: str


def _hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or token_hex(16)
    digest = pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120_000).hex()
    return f"pbkdf2_sha256$120000${salt}${digest}"


def _verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, rounds, salt, expected = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        actual = pbkdf2_hmac("sha256", password.encode(), salt.encode(), int(rounds)).hex()
        return compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


@router.post("/signup")
def signup(request: AuthRequest, db: Session = Depends(get_db)):
    email = str(request.email).strip().lower()
    if len(request.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")
    if db.query(models.User).filter(models.User.email == email).first():
        raise HTTPException(status_code=409, detail="This email is already registered. Please login.")
    db.add(models.User(email=email, password_hash=_hash_password(request.password)))
    db.commit()
    return {"email": email, "message": "Account created."}


@router.post("/login")
def login(request: AuthRequest, db: Session = Depends(get_db)):
    email = str(request.email).strip().lower()
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not _verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    return {"email": email, "message": "Login successful."}
