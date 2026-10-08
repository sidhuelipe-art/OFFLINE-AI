from pathlib import Path
from uuid import uuid4
import html
import json
import mimetypes
import re
import subprocess

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.database import get_db
from backend import models
from backend.routers.dependencies import get_owner_email

router = APIRouter(prefix="/files", tags=["Files"])
UPLOAD_DIR = Path(__file__).resolve().parents[1] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MAX_UPLOAD_BYTES = 25 * 1024 * 1024
MAX_CONTEXT_CHARS = 120_000


def _safe_filename(filename: str | None) -> str:
    name = Path(filename or "uploaded_file").name.strip()
    return name or "uploaded_file"


def _extract_text(path: Path, filename: str, content_type: str | None) -> str:
    suffix = path.suffix.lower()
    text_extensions = {".txt", ".md", ".markdown", ".csv", ".tsv", ".json", ".html", ".htm", ".xml", ".log", ".py", ".js", ".ts", ".css", ".yaml", ".yml"}
    if suffix in text_extensions or (content_type and content_type.startswith("text/")):
        raw = path.read_text(encoding="utf-8", errors="replace")
        if suffix in {".html", ".htm"}:
            raw = re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>|<[^>]+>", " ", raw, flags=re.IGNORECASE)
            raw = html.unescape(raw)
        elif suffix == ".json":
            try:
                raw = json.dumps(json.loads(raw), ensure_ascii=False, indent=2)
            except json.JSONDecodeError:
                pass
        return raw[:MAX_CONTEXT_CHARS]
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
            extracted = "\n\n".join(page.extract_text() or "" for page in PdfReader(str(path)).pages).strip()
            if extracted:
                return extracted[:MAX_CONTEXT_CHARS]
        except Exception:
            pass
        try:
            fallback = subprocess.run(["pdftotext", "-layout", str(path), "-"], capture_output=True, text=True, timeout=20)
            return (fallback.stdout or "")[:MAX_CONTEXT_CHARS]
        except (OSError, subprocess.SubprocessError):
            return ""
    if suffix == ".docx":
        try:
            from docx import Document
            return "\n".join(paragraph.text for paragraph in Document(str(path)).paragraphs)[:MAX_CONTEXT_CHARS]
        except Exception:
            return ""
    return ""


def context_path(file_path: str) -> Path:
    return Path(f"{file_path}.context.txt")


def resolve_uploaded_file(file_path: str) -> Path | None:
    upload_root = UPLOAD_DIR.resolve()
    stored_path = Path(file_path)
    for candidate in (stored_path, UPLOAD_DIR / stored_path.name):
        resolved_path = candidate.resolve()
        if upload_root in resolved_path.parents and resolved_path.is_file():
            return resolved_path
    return None


@router.post("/upload")
async def upload_file(file: UploadFile = File(...), owner_email: str = Depends(get_owner_email), db: Session = Depends(get_db)):
    original_name = _safe_filename(file.filename)
    payload = await file.read()
    if len(payload) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File is too large. Maximum size is 25 MB.")
    stored_path = UPLOAD_DIR / f"{uuid4().hex}_{original_name}"
    stored_path.write_bytes(payload)
    extracted_text = _extract_text(stored_path, original_name, file.content_type)
    context_path(str(stored_path)).write_text(extracted_text, encoding="utf-8")
    db_file = models.FileMetadata(owner_email=owner_email, filename=original_name, filepath=str(stored_path), file_type=file.content_type or mimetypes.guess_type(original_name)[0] or "application/octet-stream")
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    is_image = (file.content_type or "").startswith("image/") or stored_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}
    return {"file_id": db_file.id, "filename": original_name, "status": "uploaded", "extractable": bool(extracted_text.strip()), "previewable": True, "is_image": is_image, "is_pdf": stored_path.suffix.lower() == ".pdf", "download_url": f"/files/{db_file.id}/download", "message": "File uploaded and ready for questions." if extracted_text.strip() else "File uploaded, but no readable text was found.", "text_preview": extracted_text[:500]}


@router.get("/")
def list_files(owner_email: str = Depends(get_owner_email), db: Session = Depends(get_db)):
    records = db.query(models.FileMetadata).filter(models.FileMetadata.owner_email == owner_email).order_by(models.FileMetadata.uploaded_at.desc()).all()
    files = []
    paths_updated = False
    for record in records:
        path = resolve_uploaded_file(record.filepath)
        if path and record.filepath != str(path):
            record.filepath = str(path)
            paths_updated = True
        files.append({"file_id": record.id, "filename": record.filename, "file_type": record.file_type, "uploaded_at": record.uploaded_at, "download_url": f"/files/{record.id}/download", "available": path is not None})
    if paths_updated:
        db.commit()
    return files


@router.get("/{file_id}/download")
def download_file(file_id: int, owner_email: str = Depends(get_owner_email), db: Session = Depends(get_db)):
    record = db.query(models.FileMetadata).filter(models.FileMetadata.id == file_id, models.FileMetadata.owner_email == owner_email).first()
    if not record:
        raise HTTPException(status_code=404, detail="File not found.")
    path = resolve_uploaded_file(record.filepath)
    if not path:
        raise HTTPException(status_code=404, detail="Uploaded file is no longer available.")
    if record.filepath != str(path):
        record.filepath = str(path)
        db.commit()
    return FileResponse(path=str(path), filename=record.filename, media_type=record.file_type or "application/octet-stream")
