from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from backend.services.voice_service import voice_service
from backend.routers.dependencies import get_owner_email
import os
import tempfile
from pathlib import Path

router = APIRouter(prefix="/voice", tags=["Voice"])
SUPPORTED_AUDIO_EXTENSIONS = {".aac", ".flac", ".m4a", ".mp3", ".mp4", ".ogg", ".opus", ".wav", ".webm", ".wma"}
MAX_AUDIO_BYTES = 25 * 1024 * 1024

def _audio_suffix(file: UploadFile) -> str:
    suffix = Path(file.filename or "").suffix.lower()
    if not (file.content_type or "").startswith("audio/") and suffix not in SUPPORTED_AUDIO_EXTENSIONS:
        raise HTTPException(status_code=415, detail="Please upload a supported audio file.")
    return suffix

async def _write_temp_audio(file: UploadFile) -> str:
    suffix = _audio_suffix(file)
    payload = await file.read(MAX_AUDIO_BYTES + 1)
    if len(payload) > MAX_AUDIO_BYTES:
        raise HTTPException(status_code=413, detail="Audio file is too large. Maximum size is 25 MB.")
    if not payload:
        raise HTTPException(status_code=400, detail="The selected audio file is empty.")
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        temp.write(payload)
        return temp.name
    finally:
        temp.close()

@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...), owner_email: str = Depends(get_owner_email)):
    temp_path = await _write_temp_audio(file)
    try:
        return {"transcription": voice_service.transcribe_audio(temp_path)}
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@router.post("/lyrics")
async def extract_lyrics(file: UploadFile = File(...), owner_email: str = Depends(get_owner_email)):
    temp_path = await _write_temp_audio(file)
    try:
        lyrics = voice_service.transcribe_lyrics(temp_path)
        if not lyrics:
            raise HTTPException(status_code=422, detail="No lyrics could be recognized. Use a clear recording with audible vocals.")
        return {"lyrics": lyrics}
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=502, detail="Could not extract lyrics from this audio. Check that the file is playable and try again.") from error
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
