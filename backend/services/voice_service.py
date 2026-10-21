import os
import threading

import pyttsx3
from faster_whisper import WhisperModel


class VoiceService:
    def __init__(self):
        # Do not download/load Whisper during application startup. Render may
        # restart the service if a model is loaded while importing the app.
        self.model_name = os.getenv("WHISPER_MODEL", "tiny")
        self.stt_model = None
        self._model_lock = threading.Lock()

    def _get_model(self):
        if self.stt_model is None:
            with self._model_lock:
                if self.stt_model is None:
                    self.stt_model = WhisperModel(
                        self.model_name,
                        device="cpu",
                        compute_type="int8",
                    )
        return self.stt_model

    def transcribe_audio(self, audio_file_path: str) -> str:
        model = self._get_model()
        segments, _ = model.transcribe(audio_file_path)
        return " ".join(segment.text for segment in segments).strip()

    def transcribe_lyrics(self, audio_file_path: str) -> str:
        model = self._get_model()
        segments, _ = model.transcribe(
            audio_file_path,
            initial_prompt=(
                "Transcribe the sung lyrics verbatim in their original language. "
                "Do not describe the music."
            ),
            vad_filter=False,
        )
        return " ".join(segment.text for segment in segments).strip()

    def text_to_speech(self, text: str, output_path: str = "output.mp3"):
        engine = pyttsx3.init()
        engine.save_to_file(text, output_path)
        engine.runAndWait()
        return output_path


voice_service = VoiceService()
