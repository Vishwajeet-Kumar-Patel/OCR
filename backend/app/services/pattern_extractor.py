import json
import logging
import httpx

from openai import AsyncOpenAI

from app.core.config import settings
from app.services.provider_errors import AIServiceError, sanitize_provider_error

logger = logging.getLogger(__name__)


def _model_path(model_name: str) -> str:
    return model_name if model_name.startswith("models/") else f"models/{model_name}"


class PatternExtractor:
    def __init__(self) -> None:
        self.provider = settings.ai_provider.lower()
        self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def extract_patterns(self, analyses: list[dict]) -> dict:
        prompt = (
            "You are a branding analyst. Based on these ad analyses, find common patterns in layout, colors, style, "
            "copy tone, and CTA usage. Return strict JSON with keys: summary, common_layouts (array), "
            "recurring_palettes (array), style_patterns (array), copy_tone, cta_patterns (array)."
        )

        if self.provider == "gemini":
            raw = await self._extract_with_gemini(prompt, analyses)
        else:
            response = await self.openai_client.chat.completions.create(
                model=settings.openai_model,
                temperature=0.3,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": "Return valid JSON only."},
                    {"role": "user", "content": f"{prompt}\n\nAd Analyses:\n{json.dumps(analyses, ensure_ascii=True)}"}
                ]
            )
            raw = response.choices[0].message.content or "{}"
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("Pattern extraction returned invalid JSON")
            return {
                "summary": "Unable to parse pattern summary",
                "common_layouts": [],
                "recurring_palettes": [],
                "style_patterns": [],
                "copy_tone": "unknown",
                "cta_patterns": []
            }

    async def _extract_with_gemini(self, prompt: str, analyses: list[dict]) -> str:
        candidate_models = [settings.gemini_model]
        if settings.gemini_fallback_model and settings.gemini_fallback_model not in candidate_models:
            candidate_models.append(settings.gemini_fallback_model)

        payload = {
            "contents": [{"parts": [{"text": f"{prompt}\n\nAd Analyses:\n{json.dumps(analyses, ensure_ascii=True)}"}]}],
            "generationConfig": {
                "temperature": 0.3,
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
