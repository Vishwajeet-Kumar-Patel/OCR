import logging
import uuid
from collections import Counter
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi import Depends
from fastapi import Request
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models import AnalysisRecord
from app.schemas.ad_schemas import AnalyzeAdsRequest, AnalyzeAdsResponse, PatternReport
from app.db.database import get_db
from app.services.ocr_service import OCRService
from app.services.pattern_extractor import PatternExtractor
from app.services.rag_service import RAGService
from app.services.storage_service import StorageService
from app.services.vision_service import VisionService
from app.services.provider_errors import AIServiceError

router = APIRouter(prefix="/ads", tags=["ads"])
logger = logging.getLogger(__name__)

ocr_service = OCRService()
vision_service = VisionService()
pattern_extractor = PatternExtractor()
storage_service = StorageService()


def get_rag_service() -> RAGService | None:
    try:
        return RAGService()
    except Exception as exc:
        logger.warning("RAG service unavailable, continuing without vector store: %s", exc)
        return None


def _fallback_pattern_report(analyses: list[dict]) -> dict:
    layout_counter: Counter[str] = Counter()
    color_counter: Counter[str] = Counter()
    style_counter: Counter[str] = Counter()
    cta_counter: Counter[str] = Counter()

    for item in analyses:
        visual = item.get("visual_description", {}) or {}
        text = item.get("extracted_text", {}) or {}

        layout = (visual.get("layout") or "").strip()
        style = (visual.get("style") or "").strip()
        cta = (text.get("cta") or "").strip()

        if layout:
            layout_counter[layout] += 1
        if style:
            style_counter[style] += 1
        if cta:
            cta_counter[cta] += 1

        for color in visual.get("colors", []) or []:
            if isinstance(color, str) and color.strip():
                color_counter[color.strip()] += 1

    return {
        "summary": "Generated using local fallback because model provider was temporarily rate-limited.",
        "common_layouts": [x for x, _ in layout_counter.most_common(3)] or ["product center with headline and CTA"],
        "recurring_palettes": [x for x, _ in color_counter.most_common(5)] or ["neutral"],
        "style_patterns": [x for x, _ in style_counter.most_common(3)] or ["clean modern"],
        "copy_tone": "short, benefit-focused",
        "cta_patterns": [x for x, _ in cta_counter.most_common(3)] or ["Shop Now"]
    }


@router.post("/analyze", response_model=AnalyzeAdsResponse)
async def analyze_ads(payload: AnalyzeAdsRequest, request: Request, db: AsyncSession = Depends(get_db)) -> AnalyzeAdsResponse:
    job_dir = Path(settings.upload_dir) / payload.job_id
    if not job_dir.exists():
        raise HTTPException(status_code=404, detail="Job not found")

    image_paths = sorted([p for p in job_dir.iterdir() if p.is_file()])
    if not image_paths:
        raise HTTPException(status_code=400, detail="No images found for job")

    db_available = bool(getattr(request.app.state, "db_available", False))
    rag_service = get_rag_service()

    analyses = []
    for image_path in image_paths:
        extracted_text = await ocr_service.extract_text(str(image_path))
        try:
            visual_description = await vision_service.describe_ad(str(image_path))
        except AIServiceError as exc:
            if exc.status_code in (429, 503):
                logger.warning("Vision unavailable for %s due to provider limits, using fallback", image_path)
                visual_description = {
                    "product_type": "unknown",
                    "layout": "unavailable_due_to_provider_limits",
                    "colors": [],
                    "style": "unknown",
                    "background": "unknown",
                    "extras": []
                }
            else:
                raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Vision analysis failed: {exc}") from exc

        analysis = {
            "image_id": str(uuid.uuid4()),
            "image_path": str(image_path),
            "extracted_text": extracted_text,
            "visual_description": visual_description
        }
        analyses.append(analysis)

        if rag_service:
            await rag_service.upsert_ad_analysis(payload.job_id, analysis)

        if db_available:
            stmt = insert(AnalysisRecord).values(
                job_id=payload.job_id,
                image_id=analysis["image_id"],
                image_path=analysis["image_path"],
                extracted_text=analysis["extracted_text"],
                visual_description=analysis["visual_description"]
            )
            await db.execute(stmt)

    if db_available:
        await db.commit()
    await storage_service.save_job_analyses(payload.job_id, analyses)

    logger.info("Analyzed %s images for job_id=%s", len(analyses), payload.job_id)
    return AnalyzeAdsResponse(analyses=analyses)


@router.post("/patterns", response_model=PatternReport)
async def extract_ad_patterns(request: AnalyzeAdsRequest) -> PatternReport:
    analyses = await storage_service.load_job_analyses(request.job_id)
    if not analyses:
        rag_service = get_rag_service()
        if rag_service:
            try:
                analyses = await rag_service.retrieve_job_context(request.job_id)
            except AIServiceError as exc:
                raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
            except Exception as exc:
                raise HTTPException(status_code=502, detail=f"RAG retrieval failed: {exc}") from exc

    if not analyses:
        raise HTTPException(status_code=404, detail="No analyses found. Run /ads/analyze first.")

    try:
        report = await pattern_extractor.extract_patterns(analyses)
    except AIServiceError as exc:
        if exc.status_code in (429, 503):
            logger.warning("Pattern extraction unavailable due to provider limits, using local fallback")
            report = _fallback_pattern_report(analyses)
        else:
            raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Pattern extraction failed: {exc}") from exc
    await storage_service.save_pattern_report(request.job_id, report)

    return PatternReport(**report)
