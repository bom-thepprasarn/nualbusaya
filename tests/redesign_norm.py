"""Undo the intended markup changes of the 22 Nov 2026 Bright Blue redesign.

The snapshot tests compare index.html with historical fixtures to catch accidental edits.
These replacements map the redesign's deliberate changes back to the old markup, so any
other difference still fails. Applied to both sides, so global replacements are safe.
"""
import re

FONT_OLD = 'https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@400;500;600&family=Noto+Serif+Thai:wght@500;600&display=swap'
FONT_NEW = 'https://fonts.googleapis.com/css2?family=Chonburi&family=Inter:wght@400;500;600&family=Noto+Sans+Thai:wght@400;500;600&family=Noto+Serif+Thai:wght@500;600&display=swap'


def undo_redesign(source):
    source = source.replace(FONT_NEW, FONT_OLD)
    source = source.replace('img/icon-blue.png', 'img/icon.png')
    # header: new pink booking button; directions became an outline button
    source = re.sub(r'\s*<a class="btn btn-book header-book"[^>]*>.*?</a>', '', source, flags=re.S)
    source = source.replace('btn btn-ghost header-directions', 'btn btn-primary')
    # hero + phone dock: the LINE link is now the pink booking button with booking wording
    source = source.replace('>จองคิว LINE</a>', '>LINE</a>')
    source = source.replace('class="btn btn-book"', 'class="btn btn-line"')
    source = source.replace('จองคิวทาง LINE', 'สอบถามคิวทาง LINE')
    return source
