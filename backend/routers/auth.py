from hashlib import pbkdf2_hmac
from hmac import compare_digest
from secrets import token_hex
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import models

router = APIRouter(prefix="/auth", tags=["Authentication"])

class AuthRequest(BaseModel):
    email: EmailStr
    password: str

def _hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or token_hex(16)
    digest = pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120_000).hex()
    return "pbkdf2_sha256$120000$" + salt + "$" + digest

def _verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, rounds, salt, expected = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        actual = pbkdf2_hmac("sha256", password.encode(), salt.encode(), int(rounds)).hex()
        return compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False

def _set_session(request: Request, email: str) -> None:
    request.session.clear()
    request.session["email"] = email

@router.post("/signup")
def signup(request: Request, auth: AuthRequest, db: Session = Depends(get_db)):
    email = str(auth.email).strip().lower()
    if len(auth.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters.")
    if db.query(models.User).filter(models.User.email == email).first():
        raise HTTPException(status_code=409, detail="This email is already registered. Please login.")
    db.add(models.User(email=email, password_hash=_hash_password(auth.password)))
    db.commit()
    _set_session(request, email)
    return {"email": email, "message": "Account created."}

@router.post("/login")
def login(request: Request, auth: AuthRequest, db: Session = Depends(get_db)):
    email = str(auth.email).strip().lower()
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not _verify_password(auth.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    _set_session(request, email)
    return {"email": email, "message": "Login successful."}

@router.get("/me")
def me(request: Request):
    email = str(request.session.get("email") or "").strip().lower()
    if not email:
        raise HTTPException(status_code=401, detail="Not authenticated.")
    return {"email": email}

@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return {"message": "Logged out."}
