from sqlalchemy import JSON, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class AnalysisRecord(Base):
    __tablename__ = "analysis_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(String(120), index=True)
    image_id: Mapped[str] = mapped_column(String(120), index=True)
    image_path: Mapped[str] = mapped_column(String(500))
    extracted_text: Mapped[dict] = mapped_column(JSON)
    visual_description: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
