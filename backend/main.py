import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.config import get_settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    s = get_settings()
    logger.info("🚀 GitHub RAG Code Analyzer starting...")
    logger.info(f"   Model: {s.openai_model} | Embeddings: {s.openai_embedding_model}")
    yield
    logger.info("🛑 Shutting down...")

def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="GitHub RAG Code Analyzer",
        description="Chat with any GitHub file using AI-powered RAG",
        version="1.0.0",
        lifespan=lifespan,
    )
    origins = ["*"] if settings.allowed_origins == "*" else settings.allowed_origins.split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router, prefix="/api")
    return app

app = create_app()
