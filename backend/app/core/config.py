from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ai_provider: str = "openai"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    vision_model: str = "gpt-4o"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    gemini_fallback_model: str = "gemini-2.0-flash"
    gemini_vision_model: str = "gemini-2.5-flash"
    gemini_embedding_model: str = "gemini-embedding-001"

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ad_prompt_ai"
    require_database: bool = False
    chroma_persist_dir: str = "./storage/chroma"
    chroma_anonymized_telemetry: bool = False
    analysis_output_dir: str = "./storage/analysis"
    upload_dir: str = "./storage/uploads"
    min_upload_images: int = 5
    max_upload_images: int = 10
    tesseract_cmd: str = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
