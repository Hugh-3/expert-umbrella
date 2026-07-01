#!/usr/bin/env python3
"""测试生成服务的新功能：反模板化约束和记忆实体注入（不依赖数据库）"""

import sys
sys.path.insert(0, '/workspace/services/novel-service')

from app.services.generation_service import (
    build_messages,
    build_anti_trope_constraints,
    build_character_context,
)
from app.models import TaskType, EntityType
from ai_engine import Message


def main():
    print("=" * 80)
    print("🚀 内容创作平台 - 反模板化约束 & 记忆实体注入 功能演示")
    print("=" * 80)
    print()

    # 模拟记忆实体数据
    class MockMemoryEntity:
        def __init__(self, entity_type, name, description, attributes=None):
            self.entity_type = entity_type
            self.name = name
            self.description = description
            self.attributes = attributes or {}

    memory_entities = [
        MockMemoryEntity(
            entity_type=EntityType.CHARACTER,
            name="李云飞",
            description="十八岁的年轻剑客，从小学剑，性格正直善良。剑术扎实但缺乏实战经验，说话前常会停顿思考。",
            attributes={"age": 18, "weapon": "师父的旧剑", "habit": "紧张时摸剑柄"}
        ),
        MockMemoryEntity(
            entity_type=EntityType.LOCATION,
            name="青石镇",
            description="位于中原与边疆交汇处的小镇，是江湖新人历练的第一站。镇子不大，街道两旁种满了槐树，夏季蝉鸣不断。",
            attributes={"位置": "中原与边疆交汇", "特色": "槐树成荫"}
        ),
        MockMemoryEntity(
            entity_type=EntityType.EVENT,
            name="李云飞下山",
            description="师父没有叮嘱，只是递给他一把旧剑。临行前师父欲言又止，似有隐情。",
            attributes={}
        ),
        MockMemoryEntity(
            entity_type=EntityType.WORLD_RULE,
            name="江湖规矩",
            description="不在老弱面前动刀、不欺没有武功的平民、不趁人之危。违背这些规矩的人会被武林同道唾弃。",
            attributes={}
        ),
    ]

    # 测试 1：角色上下文构建
    print("📖 测试 1：角色上下文构建")
    print("-" * 80)
    character_context = build_character_context(memory_entities)
    print(character_context)
    print()

    # 测试 2：反模板化约束
    print("⚠️ 测试 2：反模板化约束")
    print("-" * 80)
    anti_trope = build_anti_trope_constraints()
    print(anti_trope)
    print()

    # 测试 3：完整的消息构建
    print("📝 测试 3：完整的消息构建（含约束注入）")
    print("-" * 80)

    messages = build_messages(
        task_type=TaskType.CHAPTER,
        prompt="继续故事，写一段主角在青石镇槐树下休息的场景。要求让主角主动做出一个选择，并引入一个新的悬念。",
        context="上一章主角刚逛完镇子，买了一些干粮。天色渐暗，蝉鸣声渐渐稀疏。",
        memory_entities=memory_entities,
        previous_summary="""【第一章 初入江湖】
字数：306
核心内容：清晨，李云飞背着师父给的旧剑来到青石镇。他在街上遇到了一个白胡子老者，老者问他是否是练武之人...

【第二章 客栈风波】
字数：308
核心内容：入夜，主角住进客栈，听到隔壁桌有恶霸欺负书生。主角正准备出手时，一个神秘声音响起..."""
    )

    for i, msg in enumerate(messages):
        print(f"\n{'='*80}")
        print(f"📨 消息 {i + 1} (角色: {msg.role})")
        print(f"{'='*80}")
        content = msg.content
        # 计算字符统计
        print(f"总字符数: {len(content)}")
        print(f"包含记忆实体: {'是' if '李云飞' in content else '否'}")
        print(f"包含反模板约束: {'是' if '❌' in content else '否'}")
        print(f"包含前情摘要: {'是' if '第一章' in content else '否'}")
        print()
        print("内容预览 (前2000字符):")
        print("-" * 80)
        if len(content) > 2000:
            print(content[:2000])
            print(f"\n... [内容过长，已截断，总长度: {len(content)} 字符] ...")
        else:
            print(content)

    print()
    print("=" * 80)
    print("✅ 功能验证完成！")
    print("=" * 80)
    print()
    print("📊 功能总结:")
    print("  1. ✅ 记忆实体注入 - 角色、地点、事件、世界观设定")
    print("  2. ✅ 反模板化约束 - 禁止常见套路，强制创新")
    print("  3. ✅ 前情摘要传递 - 保持章节间连贯性")
    print("  4. ✅ 场景细节传递 - 环境描写继承")
    print()
    print("💡 实际效果:")
    print("  当连接真实的 AI 模型（如 Ollama/OpenAI）时，")
    print("  这些上下文信息会被注入到 Prompt 中，")
    print("  从而生成更符合角色设定、避免套路、")
    print("  情节连贯的高质量内容。")
    print()


if __name__ == "__main__":
    main()
