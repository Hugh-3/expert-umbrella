from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.i18n.middleware import I18nMiddleware
from app.api import projects, chapters, generate, locks, memory, feedback, export


app = FastAPI(
    title=settings.app_name,
    description="Novel creation service for content creation platform",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 国际化中间件
app.add_middleware(I18nMiddleware)

app.include_router(projects.router, prefix="/api/v1/projects", tags=["projects"])
app.include_router(chapters.router, prefix="/api/v1", tags=["chapters"])
app.include_router(generate.router, prefix="/api/v1/generate", tags=["generate"])
app.include_router(locks.router, prefix="/api/v1/locks", tags=["locks"])
app.include_router(memory.router, prefix="/api/v1/memory", tags=["memory"])
app.include_router(feedback.router, prefix="/api/v1", tags=["feedback"])
app.include_router(export.router, prefix="/api/v1/export", tags=["export"])


@app.on_event("startup")
async def startup_event():
    await init_db()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.app_name}


@app.get("/i18n/languages")
async def get_supported_languages():
    """获取支持的语言列表"""
    from app.i18n import Language, t
    return {
        "languages": [
            {"code": lang.value, "name": t(f"common.language_{lang.value}")}
            for lang in Language
        ],
        "default": "zh",
    }
