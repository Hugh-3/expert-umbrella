import pytest
import asyncio
from pathlib import Path
import tempfile
from datetime import datetime
from app.storage.database import Database

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def test_db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    db = Database(db_path)
    await db.initialize()
    yield db
    db_path.unlink(missing_ok=True)
