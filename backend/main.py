from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.logging_config import setup_logging
from app.core.config import settings
from app.db.database import Base, engine
from routes.analyze_ads import router as analyze_router
from routes.generate_prompt import router as prompt_router
from routes.upload_ads import router as upload_router


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    app.state.db_available = False
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        app.state.db_available = True
        logger.info("Database connection established and metadata tables ensured")
    except Exception as exc:
        logger.warning("Database initialization failed: %s", exc)
        if settings.require_database:
            raise
        logger.warning("Starting API without PostgreSQL metadata writes (set REQUIRE_DATABASE=true to enforce DB)")
    yield


app = FastAPI(title="Ad Prompt Intelligence API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(analyze_router)
app.include_router(prompt_router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "database_available": app.state.db_available}
