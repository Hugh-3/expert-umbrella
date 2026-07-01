"""
国际化(i18n)模块
支持多语言界面，默认中文
"""
from enum import Enum
from typing import Optional, Dict, Any, Callable
import json
import os


class Language(str, Enum):
    """支持的语言枚举"""
    ZH = "zh"  # 中文
    EN = "en"  # English
    JA = "ja"  # 日本語


class I18n:
    """国际化核心类"""

    def __init__(self, default_lang: Language = Language.ZH):
        self._default_lang = default_lang
        self._current_lang = default_lang
        self._translations: Dict[Language, Dict[str, Any]] = {}
        self._translators: list[Callable[[str, Language], str]] = []
        self._load_builtin_translations()

    def _load_builtin_translations(self):
        """加载内置翻译"""
        self._translations = {
            Language.ZH: self._get_zh_translations(),
            Language.EN: self._get_en_translations(),
            Language.JA: self._get_ja_translations(),
        }

    def set_language(self, lang: Language | str) -> None:
        """设置当前语言"""
        if isinstance(lang, str):
            lang = Language(lang)
        if lang in self._translations:
            self._current_lang = lang
        else:
            raise ValueError(f"不支持的语言: {lang}")

    def get_language(self) -> Language:
        """获取当前语言"""
        return self._current_lang

    @property
    def default_lang(self) -> Language:
        return self._default_lang

    def t(self, key: str, **kwargs) -> str:
        """
        翻译关键码

        Args:
            key: 翻译键，如 "project.not_found"
            **kwargs: 格式化参数

        Returns:
            翻译后的文本
        """
        return self._translate(key, self._current_lang, **kwargs)

    def _translate(self, key: str, lang: Language, **kwargs) -> str:
        """内部翻译方法"""
        translations = self._translations.get(lang, {})
        keys = key.split(".")
        value = translations

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                # 尝试从默认语言获取
                default_value = self._translations.get(self._default_lang, {})
                for dk in keys:
                    if isinstance(default_value, dict) and dk in default_value:
                        default_value = default_value[dk]
                    else:
                        return key
                value = default_value
                break

        if isinstance(value, str):
            if kwargs:
                return value.format(**kwargs)
            return value
        return key

    def add_translator(self, translator: Callable[[str, Language], str]) -> None:
        """添加自定义翻译器（用于动态翻译）"""
        self._translators.append(translator)

    def _get_zh_translations(self) -> Dict[str, Any]:
        """中文翻译"""
        return {
            "common": {
                "success": "操作成功",
                "error": "操作失败",
                "loading": "加载中...",
                "save": "保存",
                "cancel": "取消",
                "delete": "删除",
                "edit": "编辑",
                "create": "创建",
                "search": "搜索",
                "confirm": "确认",
                "yes": "是",
                "no": "否",
                "not_found": "未找到",
                "unauthorized": "未授权",
                "forbidden": "禁止访问",
                "internal_error": "内部错误",
                "validation_error": "验证错误",
                "language_zh": "中文",
                "language_en": "英语",
                "language_ja": "日语",
            },
            "project": {
                "name": "项目名称",
                "type": "项目类型",
                "status": "状态",
                "created_at": "创建时间",
                "updated_at": "更新时间",
                "not_found": "项目不存在",
                "created": "项目创建成功",
                "updated": "项目更新成功",
                "deleted": "项目删除成功",
                "types": {
                    "novel": "小说",
                    "music": "音乐",
                    "short_video": "短视频",
                    "micro_film": "微电影",
                },
                "statuses": {
                    "draft": "草稿",
                    "in_progress": "进行中",
                    "completed": "已完成",
                    "archived": "已归档",
                },
            },
            "chapter": {
                "title": "章节标题",
                "content": "内容",
                "word_count": "字数",
                "version": "版本",
                "order_index": "排序",
                "status": "状态",
                "not_found": "章节不存在",
                "created": "章节创建成功",
                "updated": "章节更新成功",
                "deleted": "章节删除成功",
                "statuses": {
                    "outline": "大纲",
                    "draft": "草稿",
                    "editing": "编辑中",
                    "finalized": "定稿",
                },
            },
            "version": {
                "not_found": "版本不存在",
                "rollback_success": "回滚成功",
                "rollback_failed": "回滚失败",
                "diff": "差异对比",
            },
            "generation": {
                "task_created": "生成任务已创建",
                "task_started": "生成已开始",
                "task_completed": "生成完成",
                "task_failed": "生成失败",
                "task_interrupted": "生成已中断",
                "not_found": "任务不存在",
                "interrupted": "任务已中断",
                "cannot_interrupt": "任务无法中断",
                "types": {
                    "outline": "大纲生成",
                    "chapter": "章节撰写",
                    "rewrite": "改写",
                    "polish": "润色",
                    "ideas": "创意生成",
                },
                "statuses": {
                    "queued": "排队中",
                    "running": "生成中",
                    "completed": "已完成",
                    "failed": "失败",
                    "interrupted": "已中断",
                },
            },
            "memory": {
                "entity": "记忆实体",
                "name": "名称",
                "description": "描述",
                "entity_type": "实体类型",
                "not_found": "记忆实体不存在",
                "created": "记忆创建成功",
                "updated": "记忆更新成功",
                "deleted": "记忆删除成功",
                "search": "记忆搜索",
                "extract": "实体提取",
                "types": {
                    "character": "角色",
                    "location": "地点",
                    "world_rule": "世界观",
                    "event": "事件",
                    "item": "物品",
                },
            },
            "feedback": {
                "submitted": "反馈已提交",
                "not_found": "反馈不存在",
                "overall_rating": "总体评分",
                "creativity": "创意性",
                "coherence": "连贯性",
                "style": "风格匹配",
                "character": "人物塑造",
                "issues": "问题标注",
                "comment": "评论",
            },
            "self_check": {
                "passed": "自检通过",
                "failed": "自检未通过",
                "word_count": "字数统计",
                "repetition": "重复检测",
                "sensitive_content": "敏感内容检测",
                "coherence": "连贯性检测",
                "structure": "结构检测",
            },
            "lock": {
                "acquired": "锁获取成功",
                "released": "锁释放成功",
                "conflict": "锁已被占用",
                "not_found": "锁不存在",
                "holder_mismatch": "持有者不匹配",
                "statuses": {
                    "write": "写锁",
                    "read": "读锁",
                },
            },
            "timeline": {
                "stages": {
                    "ideation": "创意构思",
                    "character_design": "人物设定",
                    "chapter_planning": "章节规划",
                    "writing": "正文撰写",
                    "editing": "编辑优化",
                    "export": "导出发布",
                },
                "statuses": {
                    "pending": "待开始",
                    "in_progress": "进行中",
                    "completed": "已完成",
                },
            },
            "errors": {
                "validation_failed": "验证失败",
                "invalid_input": "无效输入",
                "database_error": "数据库错误",
                "network_error": "网络错误",
                "ai_error": "AI服务错误",
                "unknown_error": "未知错误",
            },
        }

    def _get_en_translations(self) -> Dict[str, Any]:
        """English translations"""
        return {
            "common": {
                "success": "Success",
                "error": "Error",
                "loading": "Loading...",
                "save": "Save",
                "cancel": "Cancel",
                "delete": "Delete",
                "edit": "Edit",
                "create": "Create",
                "search": "Search",
                "confirm": "Confirm",
                "yes": "Yes",
                "no": "No",
                "not_found": "Not found",
                "unauthorized": "Unauthorized",
                "forbidden": "Forbidden",
                "internal_error": "Internal error",
                "validation_error": "Validation error",
                "language_zh": "Chinese",
                "language_en": "English",
                "language_ja": "Japanese",
            },
            "project": {
                "name": "Project Name",
                "type": "Project Type",
                "status": "Status",
                "created_at": "Created At",
                "updated_at": "Updated At",
                "not_found": "Project not found",
                "created": "Project created successfully",
                "updated": "Project updated successfully",
                "deleted": "Project deleted successfully",
                "types": {
                    "novel": "Novel",
                    "music": "Music",
                    "short_video": "Short Video",
                    "micro_film": "Micro Film",
                },
                "statuses": {
                    "draft": "Draft",
                    "in_progress": "In Progress",
                    "completed": "Completed",
                    "archived": "Archived",
                },
            },
            "chapter": {
                "title": "Chapter Title",
                "content": "Content",
                "word_count": "Word Count",
                "version": "Version",
                "order_index": "Order",
                "status": "Status",
                "not_found": "Chapter not found",
                "created": "Chapter created successfully",
                "updated": "Chapter updated successfully",
                "deleted": "Chapter deleted successfully",
                "statuses": {
                    "outline": "Outline",
                    "draft": "Draft",
                    "editing": "Editing",
                    "finalized": "Finalized",
                },
            },
            "version": {
                "not_found": "Version not found",
                "rollback_success": "Rollback successful",
                "rollback_failed": "Rollback failed",
                "diff": "Diff Comparison",
            },
            "generation": {
                "task_created": "Generation task created",
                "task_started": "Generation started",
                "task_completed": "Generation completed",
                "task_failed": "Generation failed",
                "task_interrupted": "Generation interrupted",
                "not_found": "Task not found",
                "interrupted": "Task interrupted",
                "cannot_interrupt": "Cannot interrupt task",
                "types": {
                    "outline": "Outline Generation",
                    "chapter": "Chapter Writing",
                    "rewrite": "Rewrite",
                    "polish": "Polish",
                    "ideas": "Ideas Generation",
                },
                "statuses": {
                    "queued": "Queued",
                    "running": "Running",
                    "completed": "Completed",
                    "failed": "Failed",
                    "interrupted": "Interrupted",
                },
            },
            "memory": {
                "entity": "Memory Entity",
                "name": "Name",
                "description": "Description",
                "entity_type": "Entity Type",
                "not_found": "Memory entity not found",
                "created": "Memory created successfully",
                "updated": "Memory updated successfully",
                "deleted": "Memory deleted successfully",
                "search": "Memory Search",
                "extract": "Entity Extraction",
                "types": {
                    "character": "Character",
                    "location": "Location",
                    "world_rule": "World Rule",
                    "event": "Event",
                    "item": "Item",
                },
            },
            "feedback": {
                "submitted": "Feedback submitted",
                "not_found": "Feedback not found",
                "overall_rating": "Overall Rating",
                "creativity": "Creativity",
                "coherence": "Coherence",
                "style": "Style Match",
                "character": "Characterization",
                "issues": "Issues",
                "comment": "Comment",
            },
            "self_check": {
                "passed": "Self-check passed",
                "failed": "Self-check failed",
                "word_count": "Word Count",
                "repetition": "Repetition Check",
                "sensitive_content": "Sensitive Content Check",
                "coherence": "Coherence Check",
                "structure": "Structure Check",
            },
            "lock": {
                "acquired": "Lock acquired",
                "released": "Lock released",
                "conflict": "Lock conflict",
                "not_found": "Lock not found",
                "holder_mismatch": "Holder mismatch",
                "statuses": {
                    "write": "Write Lock",
                    "read": "Read Lock",
                },
            },
            "timeline": {
                "stages": {
                    "ideation": "Ideation",
                    "character_design": "Character Design",
                    "chapter_planning": "Chapter Planning",
                    "writing": "Writing",
                    "editing": "Editing",
                    "export": "Export",
                },
                "statuses": {
                    "pending": "Pending",
                    "in_progress": "In Progress",
                    "completed": "Completed",
                },
            },
            "errors": {
                "validation_failed": "Validation failed",
                "invalid_input": "Invalid input",
                "database_error": "Database error",
                "network_error": "Network error",
                "ai_error": "AI service error",
                "unknown_error": "Unknown error",
            },
        }

    def _get_ja_translations(self) -> Dict[str, Any]:
        """日本語翻訳"""
        return {
            "common": {
                "success": "成功",
                "error": "エラー",
                "loading": "読み込み中...",
                "save": "保存",
                "cancel": "キャンセル",
                "delete": "削除",
                "edit": "編集",
                "create": "作成",
                "search": "検索",
                "confirm": "確認",
                "yes": "はい",
                "no": "いいえ",
                "not_found": "見つかりません",
                "unauthorized": "未認証",
                "forbidden": "禁止",
                "internal_error": "内部エラー",
                "validation_error": "検証エラー",
                "language_zh": "中国語",
                "language_en": "英語",
                "language_ja": "日本語",
            },
            "project": {
                "name": "プロジェクト名",
                "type": "プロジェクトタイプ",
                "status": "ステータス",
                "created_at": "作成日時",
                "updated_at": "更新日時",
                "not_found": "プロジェクトが見つかりません",
                "created": "プロジェクトが作成されました",
                "updated": "プロジェクトが更新されました",
                "deleted": "プロジェクトが削除されました",
                "types": {
                    "novel": "小説",
                    "music": "音楽",
                    "short_video": "短動画",
                    "micro_film": "マイクロフィルム",
                },
                "statuses": {
                    "draft": "下書き",
                    "in_progress": "進行中",
                    "completed": "完了",
                    "archived": "アーカイブ済み",
                },
            },
            "chapter": {
                "title": "章タイトル",
                "content": "内容",
                "word_count": "文字数",
                "version": "バージョン",
                "order_index": "順序",
                "status": "ステータス",
                "not_found": "章が見つかりません",
                "created": "章が作成されました",
                "updated": "章が更新されました",
                "deleted": "章が削除されました",
                "statuses": {
                    "outline": "アウトライン",
                    "draft": "下書き",
                    "editing": "編集中",
                    "finalized": "最終版",
                },
            },
            "version": {
                "not_found": "バージョンが見つかりません",
                "rollback_success": "ロールバック成功",
                "rollback_failed": "ロールバック失敗",
                "diff": "差分比較",
            },
            "generation": {
                "task_created": "生成タスクが作成されました",
                "task_started": "生成開始",
                "task_completed": "生成完了",
                "task_failed": "生成失敗",
                "task_interrupted": "生成中断",
                "not_found": "タスクが見つかりません",
                "interrupted": "タスクが中断されました",
                "cannot_interrupt": "タスクを中断できません",
                "types": {
                    "outline": "アウトライン生成",
                    "chapter": "章作成",
                    "rewrite": "書き直し",
                    "polish": "推敲",
                    "ideas": "アイデア生成",
                },
                "statuses": {
                    "queued": "待機中",
                    "running": "生成中",
                    "completed": "完了",
                    "failed": "失敗",
                    "interrupted": "中断済み",
                },
            },
            "memory": {
                "entity": "メモリ实体",
                "name": "名前",
                "description": "説明",
                "entity_type": "实体タイプ",
                "not_found": "メモリ实体が見つかりません",
                "created": "メモリが作成されました",
                "updated": "メモリが更新されました",
                "deleted": "メモリが削除されました",
                "search": "メモリ検索",
                "extract": "实体抽出",
                "types": {
                    "character": "キャラクター",
                    "location": "場所",
                    "world_rule": "世界ルール",
                    "event": "イベント",
                    "item": "アイテム",
                },
            },
            "feedback": {
                "submitted": "フィードバックが送信されました",
                "not_found": "フィードバックが見つかりません",
                "overall_rating": "総合評価",
                "creativity": "創造性",
                "coherence": "一貫性",
                "style": "スタイル",
                "character": "キャラクター",
                "issues": "問題",
                "comment": "コメント",
            },
            "self_check": {
                "passed": "自己チェック合格",
                "failed": "自己チェック失敗",
                "word_count": "文字数",
                "repetition": "繰り返しチェック",
                "sensitive_content": "センシティブコンテンツ",
                "coherence": "一貫性チェック",
                "structure": "構造チェック",
            },
            "lock": {
                "acquired": "ロック取得成功",
                "released": "ロック解放成功",
                "conflict": "ロック競合",
                "not_found": "ロックが見つかりません",
                "holder_mismatch": "ホルダーが一致しません",
                "statuses": {
                    "write": "書き込みロック",
                    "read": "読み取りロック",
                },
            },
            "timeline": {
                "stages": {
                    "ideation": "アイデーショ",
                    "character_design": "キャラクター設計",
                    "chapter_planning": "章計画",
                    "writing": "執筆",
                    "editing": "編集",
                    "export": "エクスポート",
                },
                "statuses": {
                    "pending": "未着手",
                    "in_progress": "進行中",
                    "completed": "完了",
                },
            },
            "errors": {
                "validation_failed": "検証失敗",
                "invalid_input": "無効な入力",
                "database_error": "データベースエラー",
                "network_error": "ネットワークエラー",
                "ai_error": "AIサービスエラー",
                "unknown_error": "不明なエラー",
            },
        }


# 全局i18n实例
i18n = I18n(default_lang=Language.ZH)


def get_i18n() -> I18n:
    """获取i18n实例"""
    return i18n


def set_language(lang: Language | str) -> None:
    """设置语言"""
    i18n.set_language(lang)


def t(key: str, **kwargs) -> str:
    """翻译辅助函数"""
    return i18n.t(key, **kwargs)
