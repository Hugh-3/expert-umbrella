import aiosqlite
from pathlib import Path
from typing import Optional, List, Dict, Any
import json

class Database:
    def __init__(self, db_path: Optional[Path] = None):
        from app.config import settings
        self.db_path = db_path or settings.db_path
    
    async def initialize(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.executescript("""
                CREATE TABLE IF NOT EXISTS evaluation_reports (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    target_project_path TEXT,
                    target_api_url TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    functionality_score REAL,
                    usability_score REAL,
                    performance_score REAL,
                    ui_design_score REAL,
                    overall_score REAL,
                    summary TEXT,
                    findings TEXT,
                    suggestions TEXT,
                    raw_metrics TEXT
                );
                
                CREATE TABLE IF NOT EXISTS optimization_plans (
                    id TEXT PRIMARY KEY,
                    evaluation_id TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    improvements TEXT,
                    code_suggestions TEXT,
                    verification_result TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (evaluation_id) REFERENCES evaluation_reports(id)
                );
                
                CREATE TABLE IF NOT EXISTS evaluation_snapshots (
                    id TEXT PRIMARY KEY,
                    evaluation_id TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    score REAL NOT NULL,
                    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (evaluation_id) REFERENCES evaluation_reports(id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_evaluation_timestamp ON evaluation_reports(timestamp);
                CREATE INDEX IF NOT EXISTS idx_optimization_evaluation ON optimization_plans(evaluation_id);
            """)
            await db.commit()
    
    async def save_evaluation(self, report: dict):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO evaluation_reports 
                (id, project_id, target_project_path, target_api_url, timestamp,
                 functionality_score, usability_score, performance_score, ui_design_score, overall_score,
                 summary, findings, suggestions, raw_metrics)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                report["id"],
                report["project_id"],
                report.get("target_project_path"),
                report["target_api_url"],
                report["timestamp"],
                report["scores"]["functionality"],
                report["scores"]["usability"],
                report["scores"]["performance"],
                report["scores"]["ui_design"],
                report["scores"]["overall"],
                report["summary"],
                json.dumps(report.get("findings", [])),
                json.dumps(report.get("suggestions", [])),
                json.dumps(report.get("raw_metrics", {}))
            ))
            await db.commit()
    
    async def get_evaluation(self, evaluation_id: str) -> Optional[dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM evaluation_reports WHERE id = ?", (evaluation_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
        return None
    
    async def get_latest_evaluation(self) -> Optional[dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM evaluation_reports ORDER BY timestamp DESC LIMIT 1"
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
        return None
    
    async def list_evaluations(self, limit: int = 10, offset: int = 0) -> list:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM evaluation_reports ORDER BY timestamp DESC LIMIT ? OFFSET ?",
                (limit, offset)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def save_optimization(self, plan: dict):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO optimization_plans 
                (id, evaluation_id, status, improvements, code_suggestions, verification_result, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                plan["id"],
                plan["evaluation_id"],
                plan["status"],
                json.dumps(plan.get("improvements", [])),
                json.dumps(plan.get("code_suggestions", [])),
                json.dumps(plan.get("verification_result")),
                plan["created_at"]
            ))
            await db.commit()
    
    async def get_optimization(self, optimization_id: str) -> Optional[dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM optimization_plans WHERE id = ?", (optimization_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
        return None
    
    async def update_optimization_status(self, optimization_id: str, status: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE optimization_plans SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (status, optimization_id)
            )
            await db.commit()
    
    async def get_trend_data(self, metric: str, days: int = 30) -> list:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT es.metric_name, es.score, er.timestamp
                FROM evaluation_snapshots es
                JOIN evaluation_reports er ON es.evaluation_id = er.id
                WHERE es.metric_name = ?
                AND er.timestamp >= datetime('now', '-' || ? || ' days')
                ORDER BY er.timestamp ASC
            """, (metric, days)) as cursor:
                rows = await cursor.fetchall()
                return [{"metric": row["metric_name"], "score": row["score"], "timestamp": row["timestamp"]} for row in rows]
    
    async def save_snapshot(self, snapshot_id: str, evaluation_id: str, metric_name: str, score: float, recorded_at: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO evaluation_snapshots (id, evaluation_id, metric_name, score, recorded_at)
                VALUES (?, ?, ?, ?, ?)
            """, (snapshot_id, evaluation_id, metric_name, score, recorded_at))
            await db.commit()

db = Database()

async def get_db() -> Database:
    return db
