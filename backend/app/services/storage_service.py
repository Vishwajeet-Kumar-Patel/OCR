import json
from pathlib import Path
from typing import Any

from app.core.config import settings


class StorageService:
    def __init__(self) -> None:
        self.analysis_dir = Path(settings.analysis_output_dir)
        self.analysis_dir.mkdir(parents=True, exist_ok=True)

    def _job_file(self, job_id: str) -> Path:
        return self.analysis_dir / f"{job_id}.json"

    async def save_job_analyses(self, job_id: str, analyses: list[dict[str, Any]]) -> None:
        payload = {"job_id": job_id, "analyses": analyses}
        self._job_file(job_id).write_text(json.dumps(payload, indent=2), encoding="utf-8")

    async def load_job_analyses(self, job_id: str) -> list[dict[str, Any]]:
        path = self._job_file(job_id)
        if not path.exists():
            return []
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload.get("analyses", [])

    async def save_pattern_report(self, job_id: str, report: dict[str, Any]) -> None:
        path = self.analysis_dir / f"{job_id}_patterns.json"
        path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    async def load_pattern_report(self, job_id: str) -> dict[str, Any] | None:
        path = self.analysis_dir / f"{job_id}_patterns.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    async def save_template(self, job_id: str, template: dict[str, Any]) -> None:
        path = self.analysis_dir / f"{job_id}_template.json"
        path.write_text(json.dumps(template, indent=2), encoding="utf-8")

    async def load_template(self, job_id: str) -> dict[str, Any] | None:
        path = self.analysis_dir / f"{job_id}_template.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))
