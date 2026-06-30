"""
pytest配置
"""
import asyncio
import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

# 设置测试数据库
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_novel_service.db"

from app.main import app
from app.core.database import engine, Base


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    """设置测试数据库"""
    # 创建表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # 清理
    await engine.dispose()
    if os.path.exists("./test_novel_service.db"):
        os.remove("./test_novel_service.db")


@pytest_asyncio.fixture(scope="function")
async def client():
    """创建测试客户端"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture(scope="function")
async def auth_headers(client: AsyncClient):
    """创建认证头（测试用）"""
    return {}
