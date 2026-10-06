from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from database import get_db
from routers.dependencies import get_owner_email

router = APIRouter(prefix="/memory", tags=["Chat History"])

@router.get("/")
def get_chat_history(owner_email: str = Depends(get_owner_email), db: Session = Depends(get_db)):
    return db.query(models.ChatMessage).filter(models.ChatMessage.owner_email == owner_email).order_by(models.ChatMessage.created_at.asc(), models.ChatMessage.id.asc()).all()

@router.delete("/conversation/{question_id}")
def delete_conversation(question_id: int, owner_email: str = Depends(get_owner_email), db: Session = Depends(get_db)):
    question = db.query(models.ChatMessage).filter(models.ChatMessage.id == question_id, models.ChatMessage.owner_email == owner_email, models.ChatMessage.role == "user").first()
    if not question: raise HTTPException(status_code=404, detail="Question not found.")
    answer = db.query(models.ChatMessage).filter(models.ChatMessage.id > question.id, models.ChatMessage.owner_email == owner_email, models.ChatMessage.role == "assistant").order_by(models.ChatMessage.id.asc()).first()
    deleted_ids = [question.id]; db.delete(question)
    if answer: deleted_ids.append(answer.id); db.delete(answer)
    db.commit()
    return {"status": "success", "deleted_ids": deleted_ids}

@router.delete("/")
def clear_chat_history(owner_email: str = Depends(get_owner_email), db: Session = Depends(get_db)):
    deleted = db.query(models.ChatMessage).filter(models.ChatMessage.owner_email == owner_email).delete(synchronize_session=False)
    db.commit()
    return {"status": "success", "deleted": deleted}
