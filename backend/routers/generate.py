from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
import models
from routers.dependencies import get_owner_email
from routers.files import UPLOAD_DIR
from services.ai_service import ai_service

router = APIRouter(prefix="/generate", tags=["Generation"])

class GenerateRequest(BaseModel):
    prompt: str


def _save_file_record(db: Session, owner_email: str, path: Path, filename: str, content_type: str) -> dict:
    record = models.FileMetadata(owner_email=owner_email, filename=filename, filepath=str(path), file_type=content_type)
    db.add(record); db.commit(); db.refresh(record)
    return {"file_id": record.id, "filename": filename, "download_url": f"/files/{record.id}/download", "file_type": content_type}


def _make_simple_pdf(content: str, path: Path) -> None:
    lines = []
    for paragraph in content.splitlines() or [content]:
        clean = paragraph.strip()
        while len(clean) > 92:
            cut = clean.rfind(" ", 0, 92) or 92
            lines.append(clean[:cut]); clean = clean[cut:].lstrip()
        lines.append(clean)
    lines = lines[:48] or ["Generated document"]
    def pdf_text(value):
        return value.encode("latin-1", "replace").decode("latin-1").replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    commands = ["BT", "/F1 11 Tf", "50 760 Td"]
    for index, line in enumerate(lines):
        if index: commands.append("0 -14 Td")
        commands.append(f"({pdf_text(line)}) Tj")
    commands.append("ET")
    stream = "\n".join(commands).encode("latin-1")
    objects = [b"<< /Type /Catalog /Pages 2 0 R >>", b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>", b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>", b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>", b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream"]
    pdf = bytearray(b"%PDF-1.4\n"); offsets = [0]
    for number, obj in enumerate(objects, 1):
        offsets.append(len(pdf)); pdf.extend(f"{number} 0 obj\n".encode()); pdf.extend(obj); pdf.extend(b"\nendobj\n")
    xref = len(pdf); pdf.extend(f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]: pdf.extend(f"{offset:010d} 00000 n \n".encode())
    pdf.extend(f"trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    path.write_bytes(pdf)


@router.post("/pdf")
def generate_pdf(request: GenerateRequest, owner_email: str = Depends(get_owner_email), db: Session = Depends(get_db)):
    try:
        content = ai_service.generate_response(request.prompt, "Create a clear, well-structured document for the user's PDF request. Return only the document text, with a title and useful sections.")
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"PDF content generation failed: {error}") from error
    filename = f"generated_document_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:6]}.pdf"
    path = UPLOAD_DIR / filename
    _make_simple_pdf(content, path)
    return {"kind": "pdf", "prompt": request.prompt, **_save_file_record(db, owner_email, path, filename, "application/pdf")}
