from pathlib import Path
from typing import Iterable

from fastapi import HTTPException, UploadFile

from app.core.config import settings


ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def validate_image_file(file: UploadFile) -> None:
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported image type: {ext}")


def validate_image_batch(files: Iterable[UploadFile]) -> None:
    file_list = list(files)
    min_count = settings.min_upload_images
    max_count = settings.max_upload_images
    if len(file_list) < min_count or len(file_list) > max_count:
        raise HTTPException(status_code=400, detail=f"Upload between {min_count} and {max_count} images")

    for file in file_list:
        validate_image_file(file)
