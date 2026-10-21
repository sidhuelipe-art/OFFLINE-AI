
import os
import ollama


def create_ollama_client():
    host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434").strip()
    token = os.getenv("OLLAMA_PROXY_TOKEN", "").strip()

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    return ollama.Client(host=host, headers=headers)


class AIService:
    def __init__(self, model_name: str = "llama3:latest"):
        self.model_name = model_name
        self.client = create_ollama_client()

    def generate_response(
        self,
        prompt: str,
        system_prompt: str = "You are a helpful offline AI assistant.",
        images: list[str] | None = None,
    ):
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": prompt,
                **({"images": images} if images else {}),
            },
        ]

        model = (
            os.getenv("OLLAMA_VISION_MODEL", "llava")
            if images
            else self.model_name
        )

        response = self.client.chat(model=model, messages=messages)
        return response["message"]["content"]

    def stream_response(self, messages: list):
        has_images = any(
            message.get("images")
            for message in messages
            if isinstance(message, dict)
        )

        model = (
            os.getenv("OLLAMA_VISION_MODEL", "llava")
            if has_images
            else self.model_name
        )

        response_stream = self.client.chat(
            model=model,
            messages=messages,
            stream=True,
        )

        for chunk in response_stream:
            yield chunk["message"]["content"]


ai_service = AIService()
