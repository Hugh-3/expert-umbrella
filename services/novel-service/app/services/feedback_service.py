import uuid
from typing import List, Optional

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Feedback, GenerationTask
from app.schemas import FeedbackCreate, SelfCheckResponse, SelfCheckItem


async def create_feedback(
    db: AsyncSession,
    feedback_in: FeedbackCreate,
) -> Feedback:
    feedback = Feedback(
        task_id=feedback_in.task_id,
        overall_rating=feedback_in.overall_rating,
        creativity_rating=feedback_in.creativity_rating,
        coherence_rating=feedback_in.coherence_rating,
        style_rating=feedback_in.style_rating,
        character_rating=feedback_in.character_rating,
        issues=feedback_in.issues or [],
        comment=feedback_in.comment,
    )
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)
    return feedback


async def get_feedbacks_by_task(
    db: AsyncSession,
    task_id: uuid.UUID,
) -> List[Feedback]:
    result = await db.execute(
        select(Feedback)
        .where(Feedback.task_id == task_id)
        .order_by(desc(Feedback.created_at))
    )
    return list(result.scalars().all())


async def run_self_check(
    db: AsyncSession,
    chapter_id: uuid.UUID,
) -> SelfCheckResponse:
    from app.models import Chapter

    result = await db.execute(select(Chapter).where(Chapter.id == chapter_id))
    chapter = result.scalar_one_or_none()
    if not chapter:
        return SelfCheckResponse(
            chapter_id=chapter_id,
            overall_passed=False,
            checks=[SelfCheckItem(
                check_type="chapter_exists",
                passed=False,
                details="章节不存在",
            )],
        )

    checks = []
    content = chapter.content or ""

    word_count = len(content.replace(" ", "").replace("\n", ""))
    word_check = SelfCheckItem(
        check_type="word_count",
        passed=word_count > 0,
        details=f"字数：{word_count}",
    )
    checks.append(word_check)

    has_repetition = "的的的" in content or "了了了" in content
    repetition_check = SelfCheckItem(
        check_type="repetition",
        passed=not has_repetition,
        details="未发现明显重复" if not has_repetition else "发现可能的重复内容",
    )
    checks.append(repetition_check)

    paragraphs = [p for p in content.split("\n") if p.strip()]
    structure_check = SelfCheckItem(
        check_type="structure",
        passed=len(paragraphs) >= 3,
        details=f"段落数：{len(paragraphs)}",
    )
    checks.append(structure_check)

    sensitive_words = ["敏感词1", "敏感词2"]
    has_sensitive = any(w in content for w in sensitive_words)
    sensitive_check = SelfCheckItem(
        check_type="sensitive_content",
        passed=not has_sensitive,
        details="未发现敏感内容" if not has_sensitive else "发现敏感内容",
    )
    checks.append(sensitive_check)

    coherence_check = SelfCheckItem(
        check_type="coherence",
        passed=True,
        details="连贯性检查通过（Mock模式）",
    )
    checks.append(coherence_check)

    overall = all(c.passed for c in checks)
    return SelfCheckResponse(
        chapter_id=chapter_id,
        overall_passed=overall,
        checks=checks,
    )
