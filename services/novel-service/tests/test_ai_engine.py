"""
AI Engine SDK测试
"""
import pytest
import asyncio

from ai_engine import AIEngine, Message, GenerationParams, Role, MockProvider, OpenAIProvider, OllamaProvider


class TestMockProvider:
    """Mock Provider测试"""

    @pytest.mark.asyncio
    async def test_mock_generate(self):
        """测试Mock生成"""
        provider = MockProvider()
        messages = [Message(role=Role.USER, content="写一个大纲")]
        result = await provider.generate(messages, GenerationParams())

        assert result.content
        assert result.model == "mock-model"
        assert "大纲" in result.content or "第一章" in result.content

    @pytest.mark.asyncio
    async def test_mock_stream(self):
        """测试Mock流式输出"""
        provider = MockProvider()
        messages = [Message(role=Role.USER, content="写章节")]
        chunks = []

        async for chunk in provider.stream(messages, GenerationParams()):
            chunks.append(chunk)
            if chunk.finish_reason == "stop":
                break

        assert len(chunks) > 0
        full_content = "".join(c.content for c in chunks if c.content)
        assert full_content

    @pytest.mark.asyncio
    async def test_mock_outline_response(self):
        """测试Mock大纲响应"""
        provider = MockProvider()
        messages = [Message(role=Role.USER, content="生成故事大纲")]
        result = await provider.generate(messages, GenerationParams())

        assert "大纲" in result.content
        assert "第一章" in result.content

    @pytest.mark.asyncio
    async def test_mock_chapter_response(self):
        """测试Mock章节响应"""
        provider = MockProvider()
        messages = [Message(role=Role.USER, content="写第一章内容")]
        result = await provider.generate(messages, GenerationParams())

        assert len(result.content) > 20

    @pytest.mark.asyncio
    async def test_mock_rewrite_response(self):
        """测试Mock改写响应"""
        provider = MockProvider()
        messages = [Message(role=Role.USER, content="改写这段文字")]
        result = await provider.generate(messages, GenerationParams())

        assert result.content

    @pytest.mark.asyncio
    async def test_mock_polish_response(self):
        """测试Mock润色响应"""
        provider = MockProvider()
        messages = [Message(role=Role.USER, content="润色这段内容")]
        result = await provider.generate(messages, GenerationParams())

        assert result.content


class TestAIEngine:
    """AI Engine测试"""

    @pytest.mark.asyncio
    async def test_create_mock_engine(self):
        """测试创建Mock引擎"""
        engine = AIEngine.create("mock")
        assert engine.provider is not None

    @pytest.mark.asyncio
    async def test_engine_generate(self):
        """测试引擎生成"""
        engine = AIEngine.create("mock")
        messages = [Message(role=Role.USER, content="测试")]
        result = await engine.generate(messages)

        assert result.content

    @pytest.mark.asyncio
    async def test_engine_stream(self):
        """测试引擎流式输出"""
        engine = AIEngine.create("mock")
        messages = [Message(role=Role.USER, content="测试流式")]
        chunks = []

        async for chunk in engine.stream(messages):
            chunks.append(chunk)
            if chunk.finish_reason == "stop":
                break

        assert len(chunks) > 0

    @pytest.mark.asyncio
    async def test_engine_custom_params(self):
        """测试引擎自定义参数"""
        engine = AIEngine.create("mock")
        messages = [Message(role=Role.USER, content="测试")]
        params = GenerationParams(temperature=0.5, max_tokens=100)
        result = await engine.generate(messages, params)

        assert result.content


class TestGenerationParams:
    """生成参数测试"""

    def test_default_params(self):
        """测试默认参数"""
        params = GenerationParams()
        assert params.temperature == 0.7
        assert params.max_tokens == 4096
        assert params.top_p == 1.0

    def test_custom_params(self):
        """测试自定义参数"""
        params = GenerationParams(temperature=0.9, max_tokens=1000)
        assert params.temperature == 0.9
        assert params.max_tokens == 1000


class TestMessage:
    """消息类型测试"""

    def test_user_message(self):
        """测试用户消息"""
        msg = Message(role=Role.USER, content="你好")
        assert msg.role == Role.USER
        assert msg.content == "你好"

    def test_assistant_message(self):
        """测试助手消息"""
        msg = Message(role=Role.ASSISTANT, content="你好，我是助手")
        assert msg.role == Role.ASSISTANT

    def test_system_message(self):
        """测试系统消息"""
        msg = Message(role=Role.SYSTEM, content="你是一个有帮助的助手")
        assert msg.role == Role.SYSTEM
