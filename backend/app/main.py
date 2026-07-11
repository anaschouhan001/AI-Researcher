"""ResearchGPT FastAPI application."""
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import auth, health, research
from app.core.config import get_settings
from app.core.exceptions import ResearchGPTError
from app.core.http import close_client
from app.core.logging import configure_logging, get_logger
from app.database.session import init_db

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    await init_db()
    logger.info("app.started", env=get_settings().app_env)
    yield
    await close_client()
    logger.info("app.stopped")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="ResearchGPT",
        description="AI Research Platform — multi-source research, verification, "
        "visualization, reporting and audio summaries.",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def access_log(request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        logger.info(
            "http.request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            latency_ms=round((time.perf_counter() - start) * 1000, 1),
        )
        return response

    @app.exception_handler(ResearchGPTError)
    async def domain_error_handler(request: Request, exc: ResearchGPTError):
        logger.error("domain.error", path=request.url.path, error=str(exc))
        return JSONResponse(status_code=502, content={"detail": str(exc)})

    api_prefix = "/api/v1"
    app.include_router(health.router, prefix=api_prefix)
    app.include_router(auth.router, prefix=api_prefix)
    app.include_router(research.router, prefix=api_prefix)
    return app


app = create_app()
