import asyncio
import logging
from pathlib import Path

import pytesseract
from PIL import Image

from app.core.config import settings

logger = logging.getLogger(__name__)


class OCRService:
    def __init__(self) -> None:
        pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd

    async def extract_text(self, image_path: str) -> dict:
        text = await asyncio.to_thread(self._run_tesseract, image_path)

        # Basic heuristic splitting for ad-specific fields.
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return {
            "headline": lines[0] if len(lines) > 0 else "",
            "subheadline": lines[1] if len(lines) > 1 else "",
            "cta": next((line for line in lines if any(k in line.lower() for k in ["buy", "shop", "learn", "get"])), ""),
            "offer": next((line for line in lines if any(k in line.lower() for k in ["off", "%", "free", "save"])), ""),
            "brand_name": lines[-1] if len(lines) > 2 else ""
        }

    def _run_tesseract(self, image_path: str) -> str:
        logger.info("Running OCR for image: %s", image_path)
        with Image.open(Path(image_path)) as img:
            return pytesseract.image_to_string(img)
