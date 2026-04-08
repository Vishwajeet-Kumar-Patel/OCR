import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, File, UploadFile

from app.core.config import settings
from app.utils.image_utils import validate_image_batch

router = APIRouter(prefix="/ads", tags=["ads"])
logger = logging.getLogger(__name__)


@router.post("/upload")
async def upload_ads(files: list[UploadFile] = File(...)) -> dict:
    validate_image_batch(files)

    job_id = str(uuid.uuid4())
    job_upload_dir = Path(settings.upload_dir) / job_id
    job_upload_dir.mkdir(parents=True, exist_ok=True)

    for file in files:
        file_path = job_upload_dir / (file.filename or f"{uuid.uuid4()}.png")
        content = await file.read()
        file_path.write_bytes(content)

    logger.info("Uploaded %s images for job_id=%s", len(files), job_id)
    return {"job_id": job_id, "image_count": len(files)}
