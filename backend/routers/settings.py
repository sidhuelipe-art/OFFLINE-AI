from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import models

router = APIRouter(prefix="/settings", tags=["Settings"])

@router.get("/")
def get_settings(db: Session = Depends(get_db)):
    return db.query(models.SystemSetting).all()