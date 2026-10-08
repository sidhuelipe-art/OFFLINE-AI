from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import models
from backend.routers.dependencies import get_owner_email

router = APIRouter(prefix="/settings", tags=["Settings"])

@router.get("/")
def get_settings(owner_email: str = Depends(get_owner_email), db: Session = Depends(get_db)):
    return db.query(models.SystemSetting).all()
