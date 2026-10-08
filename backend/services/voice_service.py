import pyttsx3
from faster_whisper import WhisperModel

class VoiceService:
    def __init__(self):
        # Local speech-to-text (Whisper tiny/base model for low latency)
        self.stt_model = WhisperModel("base", device="cpu", compute_type="int8")
        
    def transcribe_audio(self, audio_file_path: str) -> str:
        segments, _ = self.stt_model.transcribe(audio_file_path)
        text = " ".join([segment.text for segment in segments])
        return text.strip()

    def transcribe_lyrics(self, audio_file_path: str) -> str:
        segments, _ = self.stt_model.transcribe(
            audio_file_path,
            initial_prompt="Transcribe the sung lyrics verbatim in their original language. Do not describe the music.",
        )
        text = " ".join(segment.text for segment in segments)
        return text.strip()

    def text_to_speech(self, text: str, output_path: str = "output.mp3"):
        engine = pyttsx3.init()
        engine.save_to_file(text, output_path)
        engine.runAndWait()
        return output_path

voice_service = VoiceService()