import asyncio
import uuid
from datetime import datetime
from typing import AsyncGenerator, Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    GenerationTask,
    TaskStatus,
    TaskType,
    Chapter,
    OperationType,
    MemoryEntity,
    Project,
)
from app.schemas import GenerateRequest
from app.services.ai_service import get_ai_engine, get_generation_params
from app.services.chapter_service import create_version_snapshot, count_words
from ai_engine import Message, Role


_active_tasks: dict[uuid.UUID, bool] = {}


async def create_generation_task(
    db: AsyncSession,
    req: GenerateRequest,
) -> GenerationTask:
    from app.core.config import settings

    task = GenerationTask(
        project_id=req.project_id,
        chapter_id=req.chapter_id,
        task_type=req.task_type,
        status=TaskStatus.QUEUED,
        model=req.model or settings.ai_model,
        parameters=req.parameters or {},
        prompt=req.prompt,
        progress=0.0,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def get_generation_task(
    db: AsyncSession,
    task_id: uuid.UUID,
) -> Optional[GenerationTask]:
    result = await db.execute(
        select(GenerationTask).where(GenerationTask.id == task_id)
    )
    return result.scalar_one_or_none()


async def update_task_status(
    db: AsyncSession,
    task_id: uuid.UUID,
    status: TaskStatus,
    progress: float | None = None,
    result: str | None = None,
    error: str | None = None,
):
    task = await get_generation_task(db, task_id)
    if not task:
        return
    task.status = status
    if progress is not None:
        task.progress = progress
    if result is not None:
        task.result = result
    if error is not None:
        task.error = error
    if status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.INTERRUPTED):
        task.completed_at = datetime.utcnow()
    await db.commit()


async def get_project_memory_entities(
    db: AsyncSession,
    project_id: uuid.UUID,
    entity_types: Optional[List[str]] = None,
) -> List[MemoryEntity]:
    """获取项目的记忆实体，包括角色、地点、事件等"""
    query = select(MemoryEntity).where(MemoryEntity.project_id == project_id)
    if entity_types:
        query = query.where(MemoryEntity.entity_type.in_(entity_types))
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_previous_chapters_summary(
    db: AsyncSession,
    project_id: uuid.UUID,
    current_chapter_id: Optional[uuid.UUID] = None,
    limit: int = 2,
) -> str:
    """获取前几章的核心剧情摘要"""
    query = (
        select(Chapter)
        .where(Chapter.project_id == project_id)
        .order_by(Chapter.order_index.desc())
    )
    if current_chapter_id:
        query = query.where(Chapter.id != current_chapter_id)
    query = query.limit(limit)
    
    result = await db.execute(query)
    chapters = list(result.scalars().all())
    
    if not chapters:
        return ""
    
    summary_parts = []
    for chapter in reversed(chapters):  # 按时间顺序排列
        summary_parts.append(
            f"【{chapter.title}】\n"
            f"字数：{chapter.word_count}\n"
            f"核心内容：{chapter.content[:200]}..." if chapter.content else ""
        )
    
    return "\n\n".join(summary_parts)


def build_anti_trope_constraints() -> str:
    """构建反模板化约束"""
    return """
【⚠️ 必须避免的套路模板】
以下情节元素已被过度使用，必须避免或彻底改造：

❌ 禁止出现：
1. 师父下山前的叮嘱场景（如"江湖险恶，记住初心"）
2. "你知道我是谁吗？"、"不想活了"等标准恶霸台词
3. 神秘女子突然出现救场
4. 主角只会"好奇地看"和"皱了皱眉"作为反应
5. "悦来客栈"、"猛虎帮"等脸谱化设定
6. 书生被恶霸欺负的老套场景

✅ 替代方案：
1. 用具体的身体动作展示角色性格（如：紧张时摸剑柄、说话前先舔嘴唇）
2. 让主角主动介入冲突，而非被动旁观
3. 用环境细节暗示帮派背景（如：虎爪刀、虎纹刺青、帮规纹身）
4. 如果要出现老者/高人，必须在后续章节中有实质作用
5. 时间过渡要有场景细节呼应（如：黄昏最后一缕光 → 客栈灯火初上）

【✍️ 叙事质量要求】
1. 通过动作、环境、对话展示，而非直接说明角色性格
2. 场景描写要有"质感"：能听到声音、闻到气味、感受到温度
3. 主角必须做出至少一个影响剧情的选择或行动
4. 避免过满的对话，穿插动作描写（如：打翻碗筷、震落筷子）
5. 每章至少埋下一个后续可用的伏笔或悬念
"""


def build_character_context(memory_entities: List[MemoryEntity]) -> str:
    """根据记忆实体构建角色设定上下文"""
    if not memory_entities:
        return ""
    
    context_parts = ["【📖 项目世界观与角色设定】\n"]
    
    # 按类型分组
    characters = [e for e in memory_entities if e.entity_type.value == "character"]
    locations = [e for e in memory_entities if e.entity_type.value == "location"]
    events = [e for e in memory_entities if e.entity_type.value == "event"]
    world_rules = [e for e in memory_entities if e.entity_type.value == "world_rule"]
    items = [e for e in memory_entities if e.entity_type.value == "item"]
    
    if characters:
        context_parts.append("【人物档案】")
        for char in characters:
            attrs_str = ""
            if char.attributes:
                attrs_str = " | ".join([f"{k}={v}" for k, v in char.attributes.items()])
            context_parts.append(
                f"- {char.name}：{char.description}"
                + (f" ({attrs_str})" if attrs_str else "")
            )
        context_parts.append("")
    
    if locations:
        context_parts.append("【场景地点】")
        for loc in locations:
            context_parts.append(f"- {loc.name}：{loc.description}")
        context_parts.append("")
    
    if events:
        context_parts.append("【重要事件】")
        for evt in events:
            context_parts.append(f"- {evt.name}：{evt.description}")
        context_parts.append("")
    
    if world_rules:
        context_parts.append("【世界观设定】")
        for rule in world_rules:
            context_parts.append(f"- {rule.name}：{rule.description}")
        context_parts.append("")
    
    if items:
        context_parts.append("【关键物品】")
        for item in items:
            context_parts.append(f"- {item.name}：{item.description}")
        context_parts.append("")
    
    # 强调角色一致性的重要性
    context_parts.append("""
【⚡ 重要提醒】
- 生成内容时必须符合上述角色设定
- 人物说话方式和习惯必须与其档案一致
- 避免引入与设定矛盾的新元素
- 如果前一章有伏笔，后续章节必须呼应
""")
    
    return "\n".join(context_parts)


def build_messages(
    task_type: TaskType,
    prompt: str,
    context: str = "",
    memory_entities: Optional[List[MemoryEntity]] = None,
    previous_summary: str = "",
) -> list[Message]:
    """构建消息列表，包含反模板化约束和记忆实体注入"""
    messages = []
    
    # 构建系统提示词
    system_prompts = {
        TaskType.OUTLINE: "你是一位专业的小说创作助手，擅长生成结构清晰、情节吸引人的故事大纲。",
        TaskType.CHAPTER: "你是一位专业的小说作家，擅长撰写引人入胜的章节内容。请保持文风统一，人物形象鲜明。",
        TaskType.REWRITE: "你是一位专业的编辑，擅长改写和优化文本内容。",
        TaskType.POLISH: "你是一位文字润色专家，擅长优化语言表达，提升文字美感。",
        TaskType.IDEAS: "你是一位创意写作助手。",
    }
    
    # 基础系统提示
    base_system = system_prompts.get(task_type, "你是一位创意写作助手。")
    
    # 构建完整系统提示
    full_system = base_system
    
    # 添加记忆实体上下文
    if memory_entities:
        full_system += "\n\n" + build_character_context(memory_entities)
    
    # 添加反模板化约束（仅对章节生成）
    if task_type == TaskType.CHAPTER:
        full_system += "\n\n" + build_anti_trope_constraints()
    
    messages.append(Message(role=Role.SYSTEM, content=full_system))
    
    # 添加用户提示词
    user_content = []
    
    # 添加前几章摘要（如果有）
    if previous_summary:
        user_content.append("【前情摘要】请在以下背景基础上继续创作，确保情节连贯：\n" + previous_summary)
    
    # 添加当前上下文
    if context:
        user_content.append("【当前章节已有内容】\n" + context)
    
    # 添加用户指令
    user_content.append("【本次创作指令】\n" + prompt)
    
    messages.append(Message(role=Role.USER, content="\n\n".join(user_content)))
    
    return messages


async def stream_generation(
    db: AsyncSession,
    task_id: uuid.UUID,
) -> AsyncGenerator[dict, None]:
    task = await get_generation_task(db, task_id)
    if not task:
        yield {"event": "error", "data": {"error_code": "NOT_FOUND", "message": "任务不存在"}}
        return
    if task.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.INTERRUPTED):
        yield {"event": "error", "data": {"error_code": "ALREADY_FINISHED", "message": "任务已结束"}}
        return

    _active_tasks[task.id] = True
    await update_task_status(db, task.id, TaskStatus.RUNNING, progress=0.0)

    ai_engine = get_ai_engine()
    params = get_generation_params(task.parameters)
    context = ""
    
    # 获取当前章节内容
    if task.chapter_id:
        result = await db.execute(select(Chapter).where(Chapter.id == task.chapter_id))
        chapter = result.scalar_one_or_none()
        if chapter:
            context = chapter.content
    
    # 获取项目的记忆实体（角色、地点、事件等）
    memory_entities = await get_project_memory_entities(db, task.project_id)
    
    # 获取前几章的摘要
    previous_summary = await get_previous_chapters_summary(
        db, 
        task.project_id,
        task.chapter_id,
        limit=2
    )
    
    # 构建包含反模板约束和记忆实体注入的消息
    messages = build_messages(
        task.task_type, 
        task.prompt, 
        context,
        memory_entities,
        previous_summary
    )
    
    full_content = ""

    yield {
        "event": "start",
        "data": {"task_id": str(task.id), "model": task.model, "timestamp": datetime.utcnow().isoformat()},
    }

    position = 0
    try:
        async for chunk in ai_engine.stream(messages, params, task.model):
            if not _active_tasks.get(task.id, False):
                await update_task_status(
                    db, task.id, TaskStatus.INTERRUPTED,
                    progress=1.0, result=full_content,
                )
                yield {
                    "event": "interrupted",
                    "data": {"task_id": str(task.id), "partial_content": full_content},
                }
                return
            if chunk.content:
                full_content += chunk.content
                position += len(chunk.content)
                yield {
                    "event": "token",
                    "data": {
                        "task_id": str(task.id),
                        "content": chunk.content,
                        "position": position,
                    },
                }
            if chunk.finish_reason == "stop":
                break

        await update_task_status(
            db, task.id, TaskStatus.COMPLETED,
            progress=1.0, result=full_content,
        )

        if task.chapter_id and task.task_type in (TaskType.CHAPTER, TaskType.REWRITE, TaskType.POLISH):
            chapter_result = await db.execute(
                select(Chapter).where(Chapter.id == task.chapter_id)
            )
            chapter = chapter_result.scalar_one_or_none()
            if chapter:
                if task.task_type == TaskType.CHAPTER:
                    chapter.content = (chapter.content or "") + full_content
                else:
                    chapter.content = full_content
                chapter.word_count = count_words(chapter.content)
                chapter.version += 1
                await db.commit()
                await create_version_snapshot(
                    db, chapter.id, chapter.content,
                    OperationType.AI_GENERATE, "ai",
                )

        yield {
            "event": "done",
            "data": {
                "task_id": str(task.id),
                "final_content": full_content,
                "word_count": count_words(full_content),
            },
        }
    except Exception as e:
        await update_task_status(
            db, task.id, TaskStatus.FAILED,
            progress=1.0, error=str(e),
        )
        yield {
            "event": "error",
            "data": {"task_id": str(task.id), "error_code": "GENERATION_ERROR", "message": str(e)},
        }
    finally:
        _active_tasks.pop(task.id, None)


async def interrupt_task(db: AsyncSession, task_id: uuid.UUID) -> bool:
    task = await get_generation_task(db, task_id)
    if not task:
        return False
    if task.status not in (TaskStatus.RUNNING, TaskStatus.QUEUED):
        return False
    _active_tasks[task.id] = False
    return True
