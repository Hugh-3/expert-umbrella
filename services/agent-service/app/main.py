from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.storage.database import db, get_db
from app.api import evaluate, optimize, reports

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.initialize()
    yield

app = FastAPI(
    title="Agent Service",
    description="智能体评测与反馈系统",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(evaluate.router)
app.include_router(optimize.router)
app.include_router(reports.router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "agent-service"}

@app.get("/")
async def root():
    return {
        "service": "Agent Evaluation and Feedback System",
        "version": "0.1.0",
        "docs": "/docs"
    }
