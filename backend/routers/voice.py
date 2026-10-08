from fastapi import APIRouter, UploadFile, File, HTTPException
from services.voice_service import voice_service
import os
import shutil
import tempfile
from pathlib import Path

router = APIRouter(prefix="/voice", tags=["Voice"])
SUPPORTED_AUDIO_EXTENSIONS = {".aac", ".flac", ".m4a", ".mp3", ".mp4", ".ogg", ".opus", ".wav", ".webm", ".wma"}

@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    suffix = Path(file.filename or "").suffix
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)

        text = voice_service.transcribe_audio(temp_path)
        return {"transcription": text}
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


@router.post("/lyrics")
async def extract_lyrics(file: UploadFile = File(...)):
    suffix = Path(file.filename or "").suffix.lower()
    if not (file.content_type or "").startswith("audio/") and suffix not in SUPPORTED_AUDIO_EXTENSIONS:
        raise HTTPException(status_code=415, detail="Please upload a supported audio file.")

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)

        if os.path.getsize(temp_path) == 0:
            raise HTTPException(status_code=400, detail="The selected audio file is empty.")

        lyrics = voice_service.transcribe_lyrics(temp_path)
        if not lyrics:
            raise HTTPException(status_code=422, detail="No lyrics could be recognized. Use a clear recording with audible vocals.")
        return {"lyrics": lyrics}
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=502, detail="Could not extract lyrics from this audio. Check that the file is playable and try again.") from error
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)