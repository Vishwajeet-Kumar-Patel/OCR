import json
import logging
from typing import Any

from langchain.schema import Document

from app.vector_db.chroma_client import get_chroma_client

logger = logging.getLogger(__name__)


class RAGService:
    def __init__(self) -> None:
        self.vector_store = get_chroma_client()

    async def upsert_ad_analysis(self, job_id: str, analysis: dict[str, Any]) -> None:
        doc_text = json.dumps(analysis, ensure_ascii=True)
        doc = Document(
            page_content=doc_text,
            metadata={
                "job_id": job_id,
                "image_id": analysis.get("image_id", ""),
                "image_path": analysis.get("image_path", "")
            }
        )
        self.vector_store.add_documents([doc])
        logger.info("Inserted analysis into vector store for image_id=%s", analysis.get("image_id", ""))

    async def retrieve_job_context(self, job_id: str, query: str = "ad style and copy patterns", k: int = 10) -> list[dict]:
        docs = self.vector_store.similarity_search(query=query, k=k, filter={"job_id": job_id})
        results: list[dict] = []
        for doc in docs:
            try:
                results.append(json.loads(doc.page_content))
            except json.JSONDecodeError:
                continue
        return results
