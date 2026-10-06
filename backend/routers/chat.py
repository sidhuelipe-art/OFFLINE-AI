from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from pathlib import Path

from database import get_db
import models
from routers.dependencies import get_owner_email
from routers.files import context_path
from services.ai_service import ai_service

router = APIRouter(prefix="/chat", tags=["Chat"])
MAX_FILE_CONTEXT_CHARS = 24_000
RESPONSE_STYLE_INSTRUCTION = (
    "Answer in the same language as the user. Keep the response concise and easy to understand: "
    "start with the direct answer, usually use 2–4 short sentences or a few brief bullets, and "
    "include only the details needed to answer correctly. Avoid long introductions, repetition, "
    "and unnecessary conclusions. Format every answer consistently: do not indent ordinary "
    "paragraphs, use the same bullet marker for peer items, and indent nested bullets by exactly "
    "two spaces. Keep headings, paragraphs, and list items on separate lines. Give a fuller "
    "explanation, steps, or code when the user asks for it."
)


class ChatRequest(BaseModel):
    message: str
    system_prompt: str = "You are a helpful offline AI assistant. Keep answers brief and clear."
    file_id: int | None = None


def _save_message(db: Session, owner_email: str, role: str, content: str) -> models.ChatMessage:
    message = models.ChatMessage(owner_email=owner_email, role=role, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def _owned_file(db: Session, owner_email: str, file_id: int):
    db_file = db.query(models.FileMetadata).filter(
        models.FileMetadata.id == file_id,
        models.FileMetadata.owner_email == owner_email,
    ).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="Uploaded file was not found.")
    return db_file


def _file_context(db: Session, owner_email: str, file_id: int | None) -> str:
    if file_id is None:
        return ""
    db_file = _owned_file(db, owner_email, file_id)
    path = context_path(db_file.filepath)
    if not path.exists():
        return f"\n\nThe user attached '{db_file.filename}', but the file is no longer available. Say that clearly if relevant."
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    if not text:
        return f"\n\nThe user attached '{db_file.filename}', but no readable text could be extracted."
    return (
        f"\n\nThe user uploaded a file named '{db_file.filename}'. Answer using the file content below. "
        "If the answer is not in the file, say so clearly and do not invent facts.\n"
        f"--- FILE CONTENT ---\n{text[:MAX_FILE_CONTEXT_CHARS]}\n--- END FILE CONTENT ---"
    )


def _messages(request: ChatRequest, owner_email: str, db: Session) -> list[dict]:
    user_message = {"role": "user", "content": request.message}
    if request.file_id is not None:
        db_file = _owned_file(db, owner_email, request.file_id)
        image_path = Path(db_file.filepath)
        if image_path.is_file() and (db_file.file_type or "").startswith("image/"):
            user_message["images"] = [str(image_path)]
    return [
        {"role": "system", "content": request.system_prompt + _file_context(db, owner_email, request.file_id) + "\n\n" + RESPONSE_STYLE_INSTRUCTION},
        user_message,
    ]


@router.post("")
def chat_endpoint(request: ChatRequest, owner_email: str = Depends(get_owner_email), db: Session = Depends(get_db)):
    _save_message(db, owner_email, "user", request.message)
    messages = _messages(request, owner_email, db)
    reply = ai_service.generate_response(request.message, messages[0]["content"], images=messages[1].get("images"))
    _save_message(db, owner_email, "assistant", reply)
    return {"reply": reply}


@router.post("/stream")
def chat_stream_endpoint(request: ChatRequest, owner_email: str = Depends(get_owner_email), db: Session = Depends(get_db)):
    _save_message(db, owner_email, "user", request.message)
    messages = _messages(request, owner_email, db)

    def response_generator():
        chunks = []
        try:
            for chunk in ai_service.stream_response(messages):
                chunks.append(chunk)
                yield chunk
        finally:
            reply = "".join(chunks).strip()
            if reply:
                _save_message(db, owner_email, "assistant", reply)
            db.close()

    return StreamingResponse(response_generator(), media_type="text/plain", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
