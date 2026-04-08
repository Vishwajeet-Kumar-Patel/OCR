import json
import httpx

from openai import AsyncOpenAI

from app.core.config import settings
from app.services.provider_errors import AIServiceError, sanitize_provider_error


def _model_path(model_name: str) -> str:
    return model_name if model_name.startswith("models/") else f"models/{model_name}"


class PromptGenerator:
    def __init__(self) -> None:
        self.provider = settings.ai_provider.lower()
        self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def generate_template(self, pattern_report: dict) -> dict:
        prompt = (
            "Generate a reusable image-generation ad prompt template based on this pattern report. "
            "Return strict JSON with keys: template, variables (array). Variables should include "
            "[PRODUCT_NAME], [PRODUCT_BENEFIT], [CTA_TEXT], [TARGET_AUDIENCE], [HEADLINE]."
        )

        if self.provider == "gemini":
            raw = await self._generate_template_with_gemini(prompt, pattern_report)
        else:
            response = await self.openai_client.chat.completions.create(
                model=settings.openai_model,
                temperature=0.4,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": "Return valid JSON only."},
                    {"role": "user", "content": f"{prompt}\nPattern Report:\n{json.dumps(pattern_report, ensure_ascii=True)}"}
                ]
            )
            raw = response.choices[0].message.content or "{}"

        return json.loads(raw)

    async def fill_template(self, template: str, inputs: dict[str, str]) -> str:
        replaced = template
        mapping = {
            "[PRODUCT_NAME]": inputs.get("product_name", ""),
            "[PRODUCT_BENEFIT]": inputs.get("product_benefit", ""),
            "[CTA_TEXT]": inputs.get("cta_text", ""),
            "[TARGET_AUDIENCE]": inputs.get("target_audience", ""),
            "[HEADLINE]": f"{inputs.get('product_name', '')}: {inputs.get('product_benefit', '')}"
        }
        for key, value in mapping.items():
            replaced = replaced.replace(key, value)
        return replaced

    async def _generate_template_with_gemini(self, prompt: str, pattern_report: dict) -> str:
        candidate_models = [settings.gemini_model]
        if settings.gemini_fallback_model and settings.gemini_fallback_model not in candidate_models:
            candidate_models.append(settings.gemini_fallback_model)

        payload = {
            "contents": [{"parts": [{"text": f"{prompt}\nPattern Report:\n{json.dumps(pattern_report, ensure_ascii=True)}"}]}],
            "generationConfig": {
                "temperature": 0.4,
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
