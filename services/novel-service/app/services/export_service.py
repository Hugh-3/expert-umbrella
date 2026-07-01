import os
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import Project, Chapter
from app.services import get_project, get_chapters


def ensure_export_dir() -> str:
    export_dir = settings.export_temp_dir
    os.makedirs(export_dir, exist_ok=True)
    return export_dir


def sanitize_filename(name: str) -> str:
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    return name.strip() or "untitled"


async def export_project_to_epub(
    db: AsyncSession,
    project_id: uuid.UUID,
    chapter_ids: Optional[List[uuid.UUID]] = None,
) -> str:
    from ebooklib import epub

    project = await get_project(db, project_id)
    if not project:
        raise ValueError("项目不存在")

    chapters = await get_chapters(db, project_id)
    if chapter_ids:
        chapters = [c for c in chapters if c.id in chapter_ids]
    chapters = sorted(chapters, key=lambda c: c.order_index)

    if not chapters:
        raise ValueError("没有可导出的章节")

    book = epub.EpubBook()
    book.set_identifier(str(project_id))
    book.set_title(project.name)
    book.set_language("zh")
    book.add_author("Author")

    if project.cover_image:
        try:
            import base64
            cover_data = base64.b64decode(project.cover_image)
            book.set_cover("cover.jpg", cover_data)
        except Exception:
            pass

    epub_chapters = []
    toc_items = []

    intro_content = f"""
    <html>
    <head><title>{project.name}</title></head>
    <body>
    <h1>{project.name}</h1>
    <p>生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p>章节数：{len(chapters)}</p>
    </body>
    </html>
    """
    intro_chapter = epub.EpubHtml(title="简介", file_name="intro.xhtml", lang="zh")
    intro_chapter.content = intro_content
    book.add_item(intro_chapter)
    epub_chapters.append(intro_chapter)
    toc_items.append(epub.Link("intro.xhtml", "简介", "intro"))

    for i, chapter in enumerate(chapters, 1):
        file_name = f"chapter_{i}.xhtml"
        content_html = f"""
        <html>
        <head><title>{chapter.title}</title></head>
        <body>
        <h2>{chapter.title}</h2>
        <div class="chapter-content">
        {_text_to_html(chapter.content)}
        </div>
        </body>
        </html>
        """
        epub_ch = epub.EpubHtml(
            title=chapter.title,
            file_name=file_name,
            lang="zh",
        )
        epub_ch.content = content_html
        book.add_item(epub_ch)
        epub_chapters.append(epub_ch)
        toc_items.append(epub.Link(file_name, chapter.title, f"chapter_{i}"))

    style = "BODY { font-family: serif; } .chapter-content { line-height: 1.8; text-indent: 2em; }"
    nav_css = epub.EpubItem(
        uid="style_nav",
        file_name="style/nav.css",
        media_type="text/css",
        content=style,
    )
    book.add_item(nav_css)

    book.toc = tuple(toc_items)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ["nav"] + epub_chapters

    export_dir = ensure_export_dir()
    filename = f"{sanitize_filename(project.name)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.epub"
    file_path = os.path.join(export_dir, filename)

    epub.write_epub(file_path, book)
    return file_path


async def export_project_to_pdf(
    db: AsyncSession,
    project_id: uuid.UUID,
    chapter_ids: Optional[List[uuid.UUID]] = None,
) -> str:
    from fpdf import FPDF

    project = await get_project(db, project_id)
    if not project:
        raise ValueError("项目不存在")

    chapters = await get_chapters(db, project_id)
    if chapter_ids:
        chapters = [c for c in chapters if c.id in chapter_ids]
    chapters = sorted(chapters, key=lambda c: c.order_index)

    if not chapters:
        raise ValueError("没有可导出的章节")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    font_path = _get_font_path()
    if font_path and os.path.exists(font_path):
        pdf.add_font("Chinese", "", font_path)
        pdf.set_font("Chinese", size=12)
    else:
        pdf.set_font("Helvetica", size=12)

    pdf.add_page()
    pdf.set_font_size(20)
    pdf.cell(0, 20, text=project.name, ln=True, align="C")
    pdf.ln(10)
    pdf.set_font_size(12)
    pdf.cell(0, 10, text=f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")
    pdf.cell(0, 10, text=f"章节数：{len(chapters)}", ln=True, align="C")
    pdf.ln(20)

    for chapter in chapters:
        pdf.add_page()
        pdf.set_font_size(16)
        pdf.cell(0, 15, text=chapter.title, ln=True, align="C")
        pdf.ln(5)
        pdf.set_font_size(12)
        pdf.multi_cell(0, 8, text=chapter.content)

    export_dir = ensure_export_dir()
    filename = f"{sanitize_filename(project.name)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    file_path = os.path.join(export_dir, filename)

    pdf.output(file_path)
    return file_path


def _text_to_html(text: str) -> str:
    if not text:
        return ""
    paragraphs = text.split("\n\n")
    html_parts = []
    for para in paragraphs:
        para = para.strip()
        if para:
            para = para.replace("\n", "<br/>")
            html_parts.append(f"<p>{para}</p>")
    return "\n".join(html_parts)


def _get_font_path() -> Optional[str]:
    possible_paths = [
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "C:\\Windows\\Fonts\\msyh.ttc",
        "C:\\Windows\\Fonts\\simhei.ttf",
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None
