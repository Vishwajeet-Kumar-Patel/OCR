from fastapi import APIRouter, HTTPException

from app.schemas.ad_schemas import GeneratePromptRequest, GeneratePromptResponse, PromptTemplateResponse
from app.services.provider_errors import AIServiceError
from app.services.prompt_generator import PromptGenerator
from app.services.storage_service import StorageService

router = APIRouter(prefix="/prompt", tags=["prompt"])

prompt_generator = PromptGenerator()
storage_service = StorageService()


def _fallback_template() -> dict:
    return {
        "template": (
            "Create a clean modern ad for [PRODUCT_NAME]. "
            "Use a polished, social-media-ready composition with balanced spacing. "
            "Place the product in the center with realistic lighting. "
            "Add a bold headline at the top: '[HEADLINE]'. "
            "Include a short benefit callout about [PRODUCT_BENEFIT]. "
            "Add a clear CTA at the bottom: '[CTA_TEXT]'. "
            "Tone should resonate with [TARGET_AUDIENCE]."
        ),
        "variables": ["[PRODUCT_NAME]", "[PRODUCT_BENEFIT]", "[CTA_TEXT]", "[TARGET_AUDIENCE]", "[HEADLINE]"]
    }


@router.post("/template", response_model=PromptTemplateResponse)
async def build_prompt_template(request: dict) -> PromptTemplateResponse:
    job_id = request.get("job_id", "")
    if not job_id:
        raise HTTPException(status_code=400, detail="job_id is required")

    pattern_report = await storage_service.load_pattern_report(job_id)
    if not pattern_report:
        raise HTTPException(status_code=404, detail="Pattern report not found. Run /ads/patterns first.")

    try:
        template = await prompt_generator.generate_template(pattern_report)
    except AIServiceError as exc:
        if exc.status_code in (429, 503):
            template = _fallback_template()
        else:
            raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Prompt template generation failed: {exc}") from exc
    await storage_service.save_template(job_id, template)
    return PromptTemplateResponse(**template)


@router.post("/generate", response_model=GeneratePromptResponse)
async def generate_final_prompt(request: GeneratePromptRequest) -> GeneratePromptResponse:
    template_data = await storage_service.load_template(request.job_id)
    if not template_data:
        raise HTTPException(status_code=404, detail="Template not found. Run /prompt/template first.")

    final_prompt = await prompt_generator.fill_template(template_data.get("template", ""), request.inputs.model_dump())
    return GeneratePromptResponse(prompt=final_prompt)
