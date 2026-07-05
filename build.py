"""articles/*.md から docs/ に静的ブログを生成する (GitHub Pages用・依存なし)。
実行: /usr/bin/python3 build.py
"""
import html
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
ART = BASE / "articles"
OUT = BASE / "docs"
OUT.mkdir(exist_ok=True)

CSS = """body{font-family:'Hiragino Sans',sans-serif;max-width:720px;margin:0 auto;
padding:24px 16px;color:#253049;line-height:1.9;background:#fffdf8}
a{color:#c05621}h1{font-size:1.5em;line-height:1.5}h2{font-size:1.2em;border-left:4px solid #c05621;
padding-left:10px;margin-top:2em}.pr{background:#fff3e0;border:1px solid #f0c48a;border-radius:8px;
padding:8px 14px;font-size:.85em;color:#8a5a1e}.date{color:#98a1b3;font-size:.85em}
header{margin-bottom:2em}header a{text-decoration:none;color:#253049}
.site{font-weight:bold;font-size:1.1em}.desc{font-size:.85em;color:#98a1b3}
footer{margin-top:3em;font-size:.8em;color:#98a1b3;border-top:1px solid #eee;padding-top:1em}"""

HEAD = """<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><style>{css}</style></head><body>
<header><a href="./index.html"><span class="site">つむぎメモ 📚</span></a>
<div class="desc">本と暮らしとお金の「知って得した」を紡ぐメモ</div></header>"""

FOOT = """<footer>運営: やん (<a href="https://x.com/tsumugi_memo15">@tsumugi_memo15</a>)
| 本サイトはAmazonアソシエイト・プログラムおよびA8.netに参加しており、
記事内にプロモーション(PR)リンクを含む場合があります。</footer></body></html>"""


def md2html(md: str) -> str:
    out = []
    for line in md.split("\n"):
        line = line.rstrip()
        if line.startswith("# "):
            out.append(f"<h1>{html.escape(line[2:])}</h1>")
        elif line.startswith("## "):
            out.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line == "":
            out.append("")
        else:
            t = html.escape(line)
            t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2" rel="nofollow sponsored">\1</a>', t)
            t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
            out.append(f"<p>{t}</p>")
    return "\n".join(out)


posts = []
for f in sorted(ART.glob("*.md"), reverse=True):
    md = f.read_text(encoding="utf-8")
    title = md.split("\n")[0].lstrip("# ").strip()
    date = f.stem[:10]
    slug = f.stem + ".html"
    body = md2html(md)
    page = HEAD.format(title=f"{title} | つむぎメモ", css=CSS)
    page += f'<div class="pr">※本記事にはプロモーション(PR)が含まれます</div>'
    page += f'<div class="date">{date}</div>' + body + FOOT
    (OUT / slug).write_text(page, encoding="utf-8")
    posts.append((date, title, slug))

idx = HEAD.format(title="つむぎメモ | 本と暮らしとお金の知って得したメモ", css=CSS)
idx += "<h1>記事一覧</h1>"
for date, title, slug in posts:
    idx += f'<p><span class="date">{date}</span><br><a href="./{slug}">{title}</a></p>'
idx += FOOT
(OUT / "index.html").write_text(idx, encoding="utf-8")
print(f"built {len(posts)} article(s) -> docs/")
