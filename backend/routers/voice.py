from fastapi import APIRouter, UploadFile, File
from services.voice_service import voice_service
import shutil
import os

router = APIRouter(prefix="/voice", tags=["Voice"])

@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    text = voice_service.transcribe_audio(temp_path)
    os.remove(temp_path)
    return {"transcription": text}