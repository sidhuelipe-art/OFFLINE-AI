from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
import models
from routers.dependencies import get_owner_email

router = APIRouter(prefix="/reminders", tags=["Reminders"])

class ReminderCreate(BaseModel):
    title: str
    due_date: datetime

def serialize_reminder(item: models.Reminder) -> dict:
    due_date = item.due_date
    if due_date.tzinfo is None: due_date = due_date.replace(tzinfo=timezone.utc)
    else: due_date = due_date.astimezone(timezone.utc)
    return {"id": item.id, "title": item.title, "due_date": due_date.isoformat().replace("+00:00", "Z"), "completed": bool(item.completed)}

@router.get("/")
def list_reminders(owner_email: str = Depends(get_owner_email), db: Session = Depends(get_db)):
    items = db.query(models.Reminder).filter(models.Reminder.owner_email == owner_email).order_by(models.Reminder.due_date.asc()).all()
    return [serialize_reminder(item) for item in items]

@router.post("/")
def add_reminder(reminder: ReminderCreate, owner_email: str = Depends(get_owner_email), db: Session = Depends(get_db)):
    due_date = reminder.due_date
    if due_date.tzinfo is not None: due_date = due_date.astimezone(timezone.utc).replace(tzinfo=None)
    item = models.Reminder(owner_email=owner_email, title=reminder.title.strip(), due_date=due_date)
    db.add(item); db.commit(); db.refresh(item)
    return serialize_reminder(item)

@router.delete("/{reminder_id}")
def delete_reminder(reminder_id: int, owner_email: str = Depends(get_owner_email), db: Session = Depends(get_db)):
    item = db.query(models.Reminder).filter(models.Reminder.id == reminder_id, models.Reminder.owner_email == owner_email).first()
    if item is None: raise HTTPException(status_code=404, detail="Reminder not found")
    db.delete(item); db.commit()
    return {"message": "Reminder deleted", "id": reminder_id}
