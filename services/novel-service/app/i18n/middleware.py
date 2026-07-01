"""
国际化中间件
从请求中自动检测语言设置
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.i18n import Language, set_language, get_i18n


class I18nMiddleware(BaseHTTPMiddleware):
    """国际化中间件，自动检测语言"""

    async def dispatch(self, request: Request, call_next) -> Response:
        # 从请求头获取语言设置
        lang = self._detect_language(request)

        # 保存到请求状态中
        request.state.lang = lang

        # 设置全局语言
        try:
            set_language(lang)
        except ValueError:
            set_language(Language.ZH)

        response = await call_next(request)
        return response

    def _detect_language(self, request: Request) -> Language:
        """检测语言"""
        # 1. 优先从查询参数获取 ?lang=zh
        lang_param = request.query_params.get("lang")
        if lang_param:
            try:
                return Language(lang_param)
            except ValueError:
                pass

        # 2. 从请求头获取 Accept-Language
        accept_language = request.headers.get("accept-language", "")
        if accept_language:
            lang = self._parse_accept_language(accept_language)
            if lang:
                return lang

        # 3. 从 Cookie 获取
        lang_cookie = request.cookies.get("lang")
        if lang_cookie:
            try:
                return Language(lang_cookie)
            except ValueError:
                pass

        # 4. 默认语言
        return get_i18n().default_lang

    def _parse_accept_language(self, accept_language: str) -> Language | None:
        """解析 Accept-Language 头"""
        # 支持的优先级列表
        priority = [
            Language.ZH,  # 优先级: 中文
            Language.EN,
            Language.JA,
        ]

        # 简单解析，只取第一个
        parts = accept_language.split(",")
        for part in parts:
            code = part.split(";")[0].strip().lower()
            # 处理如 "zh-CN", "zh-Hans", "zh"
            if code.startswith("zh"):
                return Language.ZH
            elif code.startswith("en"):
                return Language.EN
            elif code.startswith("ja"):
                return Language.JA

        return None


def get_current_language(request: Request) -> Language:
    """从请求中获取当前语言"""
    if hasattr(request.state, "lang"):
        return request.state.lang
    return Language.ZH
