from google import genai

from .config import get_settings


class GeminiServiceError(RuntimeError):
    pass


class GeminiService:
    def __init__(self):
        settings = get_settings()
        self.settings = settings
        self.client = genai.Client(api_key=settings.gemini_api_key) if settings.gemini_api_key else None

    def generate(self, *, model: str, prompt: str, max_output_tokens: int) -> str:
        if not self.client:
            raise GeminiServiceError(
                "Gemini is not configured. Add GEMINI_API_KEY to your .env file."
            )

        try:
            response = self.client.models.generate_content(
                model=model,
                contents=prompt,
                config={
                    "temperature": 0.4,
                    "max_output_tokens": max_output_tokens,
                },
            )
            text = getattr(response, "text", None)
            if not text or not text.strip():
                raise GeminiServiceError("Gemini returned an empty response.")
            return text.strip()
        except GeminiServiceError:
            raise
        except Exception as exc:
            raise GeminiServiceError(f"Gemini request failed: {exc}") from exc
