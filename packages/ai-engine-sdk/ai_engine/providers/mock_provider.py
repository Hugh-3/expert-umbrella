import asyncio
from typing import AsyncGenerator, List

from ai_engine.providers.base import BaseProvider
from ai_engine.types import Message, GenerationParams, GenerationResult, StreamChunk


MOCK_RESPONSES = {
    "outline": """# 故事大纲

## 第一幕：启程
- 第一章：主角登场
- 第二章：意外发现
- 第三章：踏上旅途

## 第二幕：冒险
- 第四章：初次试炼
- 第五章：结识伙伴
- 第六章：遭遇挫折

## 第三幕：高潮与结局
- 第七章：最终决战
- 第八章：真相大白
- 第九章：新的开始""",
    "chapter": """第一章 晨曦之地

清晨的阳光透过薄雾，洒在古老的青石板路上。林远背着简单的行囊，踏上了前往远方的旅途。他不知道前方等待着他的将是什么，但他知道，这是他必须走的路。

村口的老槐树下，几位老人正在闲聊。看到林远经过，纷纷停下了话头。

"小远啊，真的要走吗？"张爷爷拄着拐杖，声音有些沙哑。

林远停下脚步，回头望了一眼这个生活了十八年的小村庄，点了点头："张爷爷，我已经决定了。"

"唉，也好，也好。"张爷爷叹了口气，"年轻人就该出去闯闯。不过记住，无论走到哪里都别忘了本心。"

"我记住了。"林远深深鞠了一躬，转身大步向前走去。

前方的路还很长，但他的心中充满了希望和期待。

太阳越升越高，驱散了最后一丝雾气，照亮了前行的道路。""",
    "rewrite": """经过修改后的段落，语句更加流畅，意境更加深远。文字经过精心润色，让读者仿佛身临其境般感受到故事的人物的情感与场景的氛围和氛围中。""",
    "polish": """经过润色后的文字，语言更加优美，节奏更加明快，读起来朗朗上口。每个字都经过推敲打磨，每个句子都承载着深厚的情感。人物形象更加鲜明，场景描写更加细腻，让读者仿佛置身于故事之中。""",
    "default": "这是一段Mock生成的文本内容。用于测试和开发环境。",
}


class MockProvider(BaseProvider):
    def __init__(self, model: str = "mock-model"):
        self.model = model

    def _get_mock_content(self, messages: List[Message]) -> str:
        if not messages:
            return MOCK_RESPONSES["default"]
        last_user_msg = ""
        for msg in reversed(messages):
            if msg.role == "user":
                last_user_msg = msg.content
                break
        content_lower = last_user_msg.lower()
        if "大纲" in last_user_msg or "outline" in content_lower:
            return MOCK_RESPONSES["outline"]
        elif "章节" in last_user_msg or "chapter" in content_lower or "续写" in last_user_msg:
            return MOCK_RESPONSES["chapter"]
        elif "改写" in last_user_msg or "rewrite" in content_lower:
            return MOCK_RESPONSES["rewrite"]
        elif "润色" in last_user_msg or "polish" in content_lower:
            return MOCK_RESPONSES["polish"]
        return MOCK_RESPONSES["default"]

    async def generate(
        self,
        messages: List[Message],
        params: GenerationParams,
        model: str = "",
    ) -> GenerationResult:
        content = self._get_mock_content(messages)
        return GenerationResult(
            content=content,
            model=model or self.model,
            prompt_tokens=len(str(messages)),
            completion_tokens=len(content),
            total_tokens=len(str(messages)) + len(content),
            finish_reason="stop",
        )

    async def stream(
        self,
        messages: List[Message],
        params: GenerationParams,
        model: str = "",
    ) -> AsyncGenerator[StreamChunk, None]:
        content = self._get_mock_content(messages)
        chunk_size = 20
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i + chunk_size]
            await asyncio.sleep(0.05)
            yield StreamChunk(
                content=chunk,
                model=model or self.model,
                finish_reason=None,
            )
        yield StreamChunk(
            content="",
            model=model or self.model,
            finish_reason="stop",
        )
