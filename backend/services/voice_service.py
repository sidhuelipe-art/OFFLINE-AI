"""Voice services with lazy loading for Render-friendly startup."""

class VoiceService:
    def __init__(self):
        self.stt_model = None

    def _model(self):
        from faster_whisper import WhisperModel

        if self.stt_model is None:
            self.stt_model = WhisperModel("base", device="cpu", compute_type="int8")
        return self.stt_model

    def transcribe_audio(self, audio_file_path: str) -> str:
        segments, _ = self._model().transcribe(audio_file_path)
        return " ".join(segment.text for segment in segments).strip()

    def transcribe_lyrics(self, audio_file_path: str) -> str:
        segments, _ = self._model().transcribe(
            audio_file_path,
            initial_prompt="Transcribe the sung lyrics verbatim in their original language. Do not describe the music.",
        )
        return " ".join(segment.text for segment in segments).strip()

    def text_to_speech(self, text: str, output_path: str = "output.mp3"):
        import pyttsx3

        engine = pyttsx3.init()
        engine.save_to_file(text, output_path)
        engine.runAndWait()
        return output_path


voice_service = VoiceService()
