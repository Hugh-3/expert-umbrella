"""
API接口测试
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient


class TestHealthAPI:
    """健康检查API测试"""

    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """测试健康检查端点"""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "novel-service"


class TestLanguageAPI:
    """语言接口测试"""

    @pytest.mark.asyncio
    async def test_get_languages(self, client: AsyncClient):
        """测试获取支持的语言列表"""
        response = await client.get("/i18n/languages")
        assert response.status_code == 200
        data = response.json()
        assert "languages" in data
        assert "default" in data
        assert len(data["languages"]) == 3


class TestProjectAPI:
    """项目管理API测试"""

    @pytest.mark.asyncio
    async def test_create_project_zh(self, client: AsyncClient):
        """测试创建项目（中文）"""
        response = await client.post(
            "/api/v1/projects",
            json={"name": "测试项目", "type": "novel"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "测试项目"
        assert data["type"] == "novel"
        assert data["status"] == "draft"

    @pytest.mark.asyncio
    async def test_create_project_en(self, client: AsyncClient):
        """测试创建项目（英文）"""
        response = await client.post(
            "/api/v1/projects?lang=en",
            json={"name": "Test Project", "type": "novel"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Project"

    @pytest.mark.asyncio
    async def test_create_project_with_metadata(self, client: AsyncClient):
        """测试创建项目（带元数据）"""
        response = await client.post(
            "/api/v1/projects",
            json={
                "name": "带元数据的项目",
                "type": "novel",
                "metadata": {"genre": "玄幻", "target_audience": "年轻人"},
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["metadata"] == {"genre": "玄幻", "target_audience": "年轻人"}

    @pytest.mark.asyncio
    async def test_list_projects(self, client: AsyncClient):
        """测试获取项目列表"""
        response = await client.get("/api/v1/projects")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_get_project_not_found(self, client: AsyncClient):
        """测试获取不存在的项目"""
        response = await client.get("/api/v1/projects/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404


class TestChapterAPI:
    """章节管理API测试"""

    @pytest.mark.asyncio
    async def test_create_chapter(self, client: AsyncClient):
        """测试创建章节"""
        # 先创建项目
        project_resp = await client.post(
            "/api/v1/projects",
            json={"name": "章节测试项目", "type": "novel"},
        )
        project_id = project_resp.json()["id"]

        # 创建章节
        response = await client.post(
            f"/api/v1/projects/{project_id}/chapters",
            json={
                "title": "第一章 测试",
                "content": "这是测试内容",
                "order_index": 1,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "第一章 测试"
        assert data["content"] == "这是测试内容"
        assert data["word_count"] == 6
        assert data["version"] == 1


class TestTimelineAPI:
    """时间线API测试"""

    @pytest.mark.asyncio
    async def test_get_timeline(self, client: AsyncClient):
        """测试获取项目时间线"""
        # 创建项目
        create_response = await client.post(
            "/api/v1/projects",
            json={"name": "时间线测试项目", "type": "novel"},
        )
        project_id = create_response.json()["id"]

        # 获取时间线
        response = await client.get(f"/api/v1/projects/{project_id}/timeline")
        assert response.status_code == 200
        data = response.json()
        assert data["project_id"] == project_id
        assert "stages" in data
        assert len(data["stages"]) == 6  # 6个阶段


class TestLockAPI:
    """分布式锁API测试"""

    @pytest.mark.asyncio
    async def test_acquire_lock(self, client: AsyncClient):
        """测试获取锁"""
        response = await client.post(
            "/api/v1/locks/acquire",
            json={"resource": "test:chapter:1", "lock_type": "write", "holder": "user1"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "acquired"

    @pytest.mark.asyncio
    async def test_lock_conflict(self, client: AsyncClient):
        """测试锁冲突"""
        # user1 获取锁
        await client.post(
            "/api/v1/locks/acquire",
            json={"resource": "test:conflict", "lock_type": "write", "holder": "user1"},
        )

        # user2 尝试获取同一锁
        response = await client.post(
            "/api/v1/locks/acquire",
            json={"resource": "test:conflict", "lock_type": "write", "holder": "user2"},
        )
        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_release_lock(self, client: AsyncClient):
        """测试释放锁"""
        # 获取锁
        await client.post(
            "/api/v1/locks/acquire",
            json={"resource": "test:release", "lock_type": "write", "holder": "user1"},
        )

        # 释放锁
        response = await client.post(
            "/api/v1/locks/release",
            json={"resource": "test:release", "holder": "user1"},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_lock_status(self, client: AsyncClient):
        """测试查询锁状态"""
        # 获取锁
        await client.post(
            "/api/v1/locks/acquire",
            json={"resource": "test:status", "lock_type": "write", "holder": "user1"},
        )

        # 查询状态
        response = await client.get("/api/v1/locks/status?resource=test:status")
        assert response.status_code == 200
        data = response.json()
        assert data["locked"] is True
        assert data["holder"] == "user1"


class TestMemoryAPI:
    """记忆系统API测试"""

    @pytest.mark.asyncio
    async def test_create_memory_entity(self, client: AsyncClient):
        """测试创建记忆实体"""
        # 先创建项目
        project_resp = await client.post(
            "/api/v1/projects",
            json={"name": "记忆测试项目", "type": "novel"},
        )
        project_id = project_resp.json()["id"]

        # 创建记忆实体
        response = await client.post(
            f"/api/v1/memory/projects/{project_id}/entities",
            json={
                "entity_type": "character",
                "name": "林远",
                "description": "故事主角",
                "confidence": 0.9,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "林远"
        assert data["entity_type"] == "character"

    @pytest.mark.asyncio
    async def test_list_memory_entities(self, client: AsyncClient):
        """测试列出记忆实体"""
        # 创建项目和实体
        project_resp = await client.post(
            "/api/v1/projects",
            json={"name": "记忆测试项目2", "type": "novel"},
        )
        project_id = project_resp.json()["id"]

        await client.post(
            f"/api/v1/memory/projects/{project_id}/entities",
            json={"entity_type": "character", "name": "角色1", "confidence": 0.8},
        )
        await client.post(
            f"/api/v1/memory/projects/{project_id}/entities",
            json={"entity_type": "location", "name": "地点1", "confidence": 0.9},
        )

        # 列出所有
        response = await client.get(f"/api/v1/memory/projects/{project_id}/entities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

        # 按类型过滤
        response = await client.get(
            f"/api/v1/memory/projects/{project_id}/entities?entity_type=character"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["entity_type"] == "character"
