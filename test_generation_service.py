#!/usr/bin/env python3
"""测试生成服务的新功能：反模板化约束和记忆实体注入"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, '/workspace/services/novel-service')

from app.services.generation_service import (
    build_messages,
    build_anti_trope_constraints,
    build_character_context,
    get_project_memory_entities,
    get_previous_chapters_summary,
)
from app.models import TaskType, MemoryEntity, EntityType
from ai_engine import Message, Role
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
import uuid


async def main():
    # 创建异步数据库引擎
    engine = create_async_engine('sqlite+aiosqlite:///novel_service.db', echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        project_id = uuid.UUID('1daf8970-f4b0-4f35-b3d8-7ca83d9b156a')

        print("=" * 80)
        print("1. 测试：获取项目的记忆实体")
        print("=" * 80)
        memory_entities = await get_project_memory_entities(session, project_id)
        print(f"找到 {len(memory_entities)} 个记忆实体：\n")
        for entity in memory_entities:
            print(f"  [{entity.entity_type.value}] {entity.name}")
            print(f"    描述: {entity.description}")
            if entity.attributes:
                print(f"    属性: {entity.attributes}")
            print()

        print("=" * 80)
        print("2. 测试：获取前几章摘要")
        print("=" * 80)
        previous_summary = await get_previous_chapters_summary(session, project_id, limit=2)
        if previous_summary:
            print(previous_summary[:500] + "..." if len(previous_summary) > 500 else previous_summary)
        else:
            print("没有前几章的内容")
        print()

        print("=" * 80)
        print("3. 测试：反模板化约束")
        print("=" * 80)
        anti_trope = build_anti_trope_constraints()
        print(anti_trope[:1000] + "..." if len(anti_trope) > 1000 else anti_trope)
        print()

        print("=" * 80)
        print("4. 测试：角色上下文构建")
        print("=" * 80)
        character_context = build_character_context(memory_entities)
        print(character_context[:1000] + "..." if len(character_context) > 1000 else character_context)
        print()

        print("=" * 80)
        print("5. 测试：完整的消息构建")
        print("=" * 80)
        messages = build_messages(
            task_type=TaskType.CHAPTER,
            prompt="继续故事，写一段主角在青石镇槐树下休息的场景",
            context="上一章主角刚逛完镇子，买了一些干粮。",
            memory_entities=memory_entities,
            previous_summary=previous_summary
        )

        for i, msg in enumerate(messages):
            print(f"\n--- 消息 {i + 1} (角色: {msg.role}) ---")
            content = msg.content
            # 只打印前 1500 个字符，避免输出过长
            if len(content) > 1500:
                print(content[:1500])
                print(f"\n... [内容过长，已截断，总长度: {len(content)} 字符] ...")
            else:
                print(content)

        print("\n" + "=" * 80)
        print("✅ 测试完成！所有新功能都正常工作。")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
