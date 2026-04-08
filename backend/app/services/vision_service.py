import base64
import json
import logging
import httpx
from openai import AsyncOpenAI

from app.core.config import settings
from app.services.provider_errors import AIServiceError, sanitize_provider_error

logger = logging.getLogger(__name__)


def _model_path(model_name: str) -> str:
    return model_name if model_name.startswith("models/") else f"models/{model_name}"


class VisionService:
    def __init__(self) -> None:
        self.provider = settings.ai_provider.lower()
        self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def describe_ad(self, image_path: str) -> dict:
        logger.info("Analyzing visual design for image: %s", image_path)
        prompt = (
            "Analyze this ad image and return strict JSON with keys: "
            "product_type, layout, colors (array), style, background, extras (array)."
        )

        if self.provider == "gemini":
            raw = await self._describe_with_gemini(image_path, prompt)
        else:
            raw = await self._describe_with_openai(image_path, prompt)

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("Vision model returned non-JSON. Falling back to default structure.")
            return {
                "product_type": "unknown",
                "layout": "unknown",
                "colors": [],
                "style": "unknown",
                "background": "unknown",
                "extras": []
            }

    async def _describe_with_openai(self, image_path: str, prompt: str) -> str:
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")

        response = await self.openai_client.chat.completions.create(
            model=settings.vision_model,
            temperature=0.2,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{b64}"}
                        }
                    ]
                }
            ]
        )
        return response.choices[0].message.content or "{}"

    async def _describe_with_gemini(self, image_path: str, prompt: str) -> str:
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")

        candidate_models = [settings.gemini_vision_model]
        if settings.gemini_fallback_model and settings.gemini_fallback_model not in candidate_models:
            candidate_models.append(settings.gemini_fallback_model)

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {"inlineData": {"mimeType": "image/png", "data": b64}}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json"
            }
        }
        last_error: Exception | None = None
        for model_name in candidate_models:
            model_path = _model_path(model_name)
            url = f"https://generativelanguage.googleapis.com/v1beta/{model_path}:generateContent?key={settings.gemini_api_key}"
            try:
                async with httpx.AsyncClient(timeout=120) as client:
                    response = await client.post(url, json=payload)
                    response.raise_for_status()
                    data = response.json()
                return data["candidates"][0]["content"]["parts"][0].get("text", "{}")
            except httpx.HTTPStatusError as exc:
                last_error = exc
                if exc.response.status_code in (404, 429, 503):
                    continue
                raise
            except Exception as exc:
                last_error = exc
                break

        exc = last_error or Exception("Unknown Gemini error")
        try:
            message = sanitize_provider_error(str(exc))
            if "API_KEY" in message or "permission" in message.lower() or "unauthorized" in message.lower():
                raise AIServiceError(f"Gemini authentication failed: {message}", status_code=401) from exc
            if "quota" in message.lower() or "429" in message:
                raise AIServiceError(f"Gemini quota exceeded: {message}", status_code=429) from exc
            raise
        finally:
            pass
