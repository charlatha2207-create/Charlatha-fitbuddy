from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from .config import get_settings
from .database import init_db
from .routes import api_router, router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    description="AI-powered personalized fitness plan generator using Gemini.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret,
    same_site="lax",
    https_only=settings.is_production,
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(router)
app.include_router(api_router)


@app.get("/health", tags=["System"])
def health():
    return {"status": "ok", "app": settings.app_name}
