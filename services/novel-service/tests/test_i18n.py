"""
国际化模块测试
"""
import pytest
from app.i18n import I18n, Language, t, set_language, get_i18n


class TestI18n:
    """i18n核心功能测试"""

    def setup_method(self):
        """每个测试前重置为中文"""
        set_language(Language.ZH)

    def test_default_language(self):
        """测试默认语言是中文"""
        i18n = get_i18n()
        assert i18n.default_lang == Language.ZH

    def test_set_language_zh(self):
        """测试设置中文"""
        set_language(Language.ZH)
        assert get_i18n().get_language() == Language.ZH

    def test_set_language_en(self):
        """测试设置英文"""
        set_language(Language.EN)
        assert get_i18n().get_language() == Language.EN

    def test_set_language_ja(self):
        """测试设置日文"""
        set_language(Language.JA)
        assert get_i18n().get_language() == Language.JA

    def test_set_invalid_language(self):
        """测试设置无效语言"""
        with pytest.raises(ValueError):
            set_language("invalid")

    def test_translate_zh(self):
        """测试中文翻译"""
        set_language(Language.ZH)
        assert t("common.success") == "操作成功"
        assert t("common.error") == "操作失败"
        assert t("project.name") == "项目名称"
        assert t("project.not_found") == "项目不存在"

    def test_translate_en(self):
        """测试英文翻译"""
        set_language(Language.EN)
        assert t("common.success") == "Success"
        assert t("common.error") == "Error"
        assert t("project.name") == "Project Name"
        assert t("project.not_found") == "Project not found"

    def test_translate_ja(self):
        """测试日文翻译"""
        set_language(Language.JA)
        assert t("common.success") == "成功"
        assert t("common.error") == "エラー"
        assert t("project.name") == "プロジェクト名"
        assert t("project.not_found") == "プロジェクトが見つかりません"

    def test_translate_with_params(self):
        """测试带参数的翻译"""
        set_language(Language.ZH)
        assert t("common.not_found") == "未找到"
        # 测试不存在的键返回键本身
        assert t("nonexistent.key") == "nonexistent.key"

    def test_translate_project_types(self):
        """测试项目类型翻译"""
        set_language(Language.ZH)
        assert t("project.types.novel") == "小说"
        assert t("project.types.music") == "音乐"
        assert t("project.types.short_video") == "短视频"
        assert t("project.types.micro_film") == "微电影"

        set_language(Language.EN)
        assert t("project.types.novel") == "Novel"
        assert t("project.types.music") == "Music"

    def test_translate_project_statuses(self):
        """测试项目状态翻译"""
        set_language(Language.ZH)
        assert t("project.statuses.draft") == "草稿"
        assert t("project.statuses.in_progress") == "进行中"
        assert t("project.statuses.completed") == "已完成"
        assert t("project.statuses.archived") == "已归档"

    def test_translate_chapter_statuses(self):
        """测试章节状态翻译"""
        set_language(Language.ZH)
        assert t("chapter.statuses.outline") == "大纲"
        assert t("chapter.statuses.draft") == "草稿"
        assert t("chapter.statuses.editing") == "编辑中"
        assert t("chapter.statuses.finalized") == "定稿"

    def test_translate_generation_types(self):
        """测试生成类型翻译"""
        set_language(Language.ZH)
        assert t("generation.types.outline") == "大纲生成"
        assert t("generation.types.chapter") == "章节撰写"
        assert t("generation.types.rewrite") == "改写"
        assert t("generation.types.polish") == "润色"
        assert t("generation.types.ideas") == "创意生成"

    def test_translate_generation_statuses(self):
        """测试生成状态翻译"""
        set_language(Language.ZH)
        assert t("generation.statuses.queued") == "排队中"
        assert t("generation.statuses.running") == "生成中"
        assert t("generation.statuses.completed") == "已完成"
        assert t("generation.statuses.failed") == "失败"
        assert t("generation.statuses.interrupted") == "已中断"

    def test_translate_memory_types(self):
        """测试记忆实体类型翻译"""
        set_language(Language.ZH)
        assert t("memory.types.character") == "角色"
        assert t("memory.types.location") == "地点"
        assert t("memory.types.world_rule") == "世界观"
        assert t("memory.types.event") == "事件"
        assert t("memory.types.item") == "物品"

    def test_translate_self_check(self):
        """测试自检翻译"""
        set_language(Language.ZH)
        assert t("self_check.passed") == "自检通过"
        assert t("self_check.word_count") == "字数统计"
        assert t("self_check.repetition") == "重复检测"
        assert t("self_check.sensitive_content") == "敏感内容检测"
        assert t("self_check.coherence") == "连贯性检测"

    def test_translate_timeline_stages(self):
        """测试时间线阶段翻译"""
        set_language(Language.ZH)
        assert t("timeline.stages.ideation") == "创意构思"
        assert t("timeline.stages.character_design") == "人物设定"
        assert t("timeline.stages.chapter_planning") == "章节规划"
        assert t("timeline.stages.writing") == "正文撰写"
        assert t("timeline.stages.editing") == "编辑优化"
        assert t("timeline.stages.export") == "导出发布"

    def test_translate_errors(self):
        """测试错误消息翻译"""
        set_language(Language.ZH)
        assert t("errors.validation_failed") == "验证失败"
        assert t("errors.database_error") == "数据库错误"
        assert t("errors.ai_error") == "AI服务错误"

    def test_translate_lock(self):
        """测试锁相关翻译"""
        set_language(Language.ZH)
        assert t("lock.acquired") == "锁获取成功"
        assert t("lock.released") == "锁释放成功"
        assert t("lock.conflict") == "锁已被占用"
        assert t("lock.not_found") == "锁不存在"

    def test_language_name_translations(self):
        """测试语言名称翻译"""
        set_language(Language.ZH)
        assert t("common.language_zh") == "中文"
        assert t("common.language_en") == "英语"
        assert t("common.language_ja") == "日语"

        set_language(Language.EN)
        assert t("common.language_zh") == "Chinese"
        assert t("common.language_en") == "English"
        assert t("common.language_ja") == "Japanese"

    def test_new_i18n_instance(self):
        """测试创建新的i18n实例"""
        i18n = I18n(default_lang=Language.EN)
        assert i18n.default_lang == Language.EN
        i18n.set_language(Language.JA)
        assert i18n.get_language() == Language.JA
