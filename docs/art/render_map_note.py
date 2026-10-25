"""Render the professor-facing Markdown as dependency-free, printable HTML."""
from pathlib import Path
import html
import re
import base64
import io
from PIL import Image

folder = Path(__file__).resolve().parent
source = folder / 'HANNOVER_MAP_SOURCES_AND_METHOD.md'

def inline(text):
    text = html.escape(text)
    text = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)', r'<a href="\2">\1</a>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    return re.sub(r'`([^`]+)`', r'<code>\1</code>', text)

lines = source.read_text(encoding='utf-8').splitlines()
body, index = [], 0
while index < len(lines):
    line = lines[index].strip()
    if not line:
        index += 1
        continue
    if line.startswith('#'):
        level = len(line) - len(line.lstrip('#'))
        body.append(f'<h{level}>{inline(line[level:].strip())}</h{level}>')
    elif line.startswith('|'):
        rows = []
        while index < len(lines) and lines[index].strip().startswith('|'):
            cells = [x.strip() for x in lines[index].strip().strip('|').split('|')]
            if not all(re.fullmatch(r'[-: ]+', cell) for cell in cells):
                tag = 'th' if not rows else 'td'
                rows.append('<tr>' + ''.join(f'<{tag}>{inline(c)}</{tag}>' for c in cells) + '</tr>')
            index += 1
        body.append('<table>' + ''.join(rows) + '</table>')
        continue
    elif line.startswith('- ') or re.match(r'\d+\. ', line):
        ordered = not line.startswith('- ')
        items = []
        pattern = r'^\d+\. ' if ordered else r'^- '
        while index < len(lines) and re.match(pattern, lines[index].strip()):
            items.append('<li>' + inline(re.sub(pattern, '', lines[index].strip())) + '</li>')
            index += 1
        tag = 'ol' if ordered else 'ul'
        body.append(f'<{tag}>' + ''.join(items) + f'</{tag}>')
        continue
    elif line.startswith('> '):
        body.append('<blockquote>' + inline(line[2:]) + '</blockquote>')
    else:
        paragraph = [line]
        while index + 1 < len(lines) and lines[index + 1].strip() and not lines[index + 1].startswith(('#', '|', '-', '>')):
            index += 1
            paragraph.append(lines[index].strip())
        body.append('<p>' + inline(' '.join(paragraph)) + '</p>')
    index += 1

style = '''
body{max-width:1000px;margin:48px auto;padding:0 28px;color:#182a32;background:#fff;font:16px/1.6 system-ui,sans-serif}
h1{font-size:32px;line-height:1.15;margin-bottom:24px}h2{font-size:23px;margin-top:38px;color:#145c56}
p,li{max-width:88ch}a{color:#075c75;overflow-wrap:anywhere}code{font:13px/1.5 monospace;overflow-wrap:anywhere}
table{border-collapse:collapse;width:100%;font-size:14px}th,td{border:1px solid #cdd9db;padding:10px;text-align:left;vertical-align:top}
th{background:#e8f1ef}blockquote{border-left:4px solid #33877a;padding:8px 20px;margin:20px 0;background:#f3f7f6}
figure{margin:36px 0}img{width:100%;height:auto}figcaption{font-size:13px;color:#48606a}.print{font-size:13px;color:#48606a}
@page{size:A4;margin:17mm} @media print{body{margin:0;padding:0;font-size:10pt;line-height:1.4}h1{font-size:21pt}h2{font-size:15pt;break-after:avoid}th,td{padding:5px;font-size:9pt}tr,blockquote,figure{break-inside:avoid}a{color:inherit;text-decoration:none}.print{display:none}}
'''
overview = folder / 'previews/hannover-v2-overview.bmp'
if not overview.exists():
    overview = folder / 'previews/hannover-route-overview.bmp'
figures = [(overview, 'Actual course-engine public-realm overview. Imported massing and authored surfaces; surrounding facade reconstruction is unfinished.')]
detail = folder / 'previews/hannover-v2-kroepcke.bmp'
if detail.exists():
    figures.append((detail, 'First Kröpcke architectural-detail pass with project-owned sunlight/shadows and corrected lower-level walls. This is an interpreted prototype, not a photograph.'))
for offset, (path, caption) in enumerate(figures):
    buffer = io.BytesIO()
    Image.open(path).convert('RGB').save(buffer, format='PNG')
    picture = base64.b64encode(buffer.getvalue()).decode('ascii')
    body.insert(2 + offset, '<figure><img src="data:image/png;base64,' + picture + '" alt="Actual course-engine render"><figcaption>' + caption + '</figcaption></figure>')
output = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Hannover Rush Hour — Sources and Method</title><style>' + style + '</style><body><p class="print">Professor-facing source and method note · Print with Ctrl+P</p>' + ''.join(body) + '</body></html>'
(folder / 'HANNOVER_MAP_SOURCES_AND_METHOD.html').write_text(output, encoding='utf-8')
print('Rendered printable HTML source note')
