import pytest
import pytest_asyncio
from pathlib import Path
import tempfile
from app.storage.database import Database

@pytest_asyncio.fixture
async def test_db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    db = Database(db_path)
    await db.initialize()
    yield db
    db_path.unlink(missing_ok=True)
