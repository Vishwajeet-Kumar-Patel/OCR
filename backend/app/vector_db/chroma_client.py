import os

from app.core.config import settings

if settings.chroma_anonymized_telemetry:
    os.environ["ANONYMIZED_TELEMETRY"] = "True"
else:
    os.environ["ANONYMIZED_TELEMETRY"] = "False"

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from app.vector_db.gemini_embeddings import GeminiRESTEmbeddings


def get_chroma_client(collection_name: str = "ad-patterns") -> Chroma:
    if settings.ai_provider.lower() == "gemini":
        embedding_model = GeminiRESTEmbeddings(api_key=settings.gemini_api_key, model=settings.gemini_embedding_model)
    else:
        embedding_model = OpenAIEmbeddings(model="text-embedding-3-small", api_key=settings.openai_api_key)

    return Chroma(
        collection_name=collection_name,
        embedding_function=embedding_model,
        persist_directory=settings.chroma_persist_dir
    )
