from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
from pydantic import BaseModel
from routers.dependencies import get_owner_email

router = APIRouter(prefix="/notes", tags=["Notes"])

class NoteCreate(BaseModel):
    title: str
    content: str

class NoteUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    append_content: str | None = None

@router.get("/")
def get_notes(owner_email: str = Depends(get_owner_email), db: Session = Depends(get_db)):
    return db.query(models.Note).filter(models.Note.owner_email == owner_email).order_by(models.Note.created_at.desc()).all()

@router.post("/")
def create_note(note: NoteCreate, owner_email: str = Depends(get_owner_email), db: Session = Depends(get_db)):
    db_note = models.Note(owner_email=owner_email, title=note.title.strip(), content=note.content.strip())
    db.add(db_note); db.commit(); db.refresh(db_note)
    return db_note

@router.put("/{note_id}")
def update_note(note_id: int, note: NoteUpdate, owner_email: str = Depends(get_owner_email), db: Session = Depends(get_db)):
    db_note = db.query(models.Note).filter(models.Note.id == note_id, models.Note.owner_email == owner_email).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found.")
    if note.title is not None: db_note.title = note.title.strip()
    if note.content is not None: db_note.content = note.content.strip()
    if note.append_content and note.append_content.strip():
        addition = note.append_content.strip()
        db_note.content = f"{db_note.content.rstrip()}\n\n{addition}" if db_note.content.strip() else addition
    db.commit(); db.refresh(db_note)
    return db_note
