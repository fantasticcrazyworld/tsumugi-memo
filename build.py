"""articles/*.md から docs/ に静的ブログを生成する (GitHub Pages用・依存なし)。
AI検索(GEO)対応: JSON-LD構造化データ / robots.txtでAIクローラー明示許可 /
llms.txt / sitemap.xml / RSS / メタディスクリプション。
実行: /usr/bin/python3 build.py
"""
import html
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
ART = BASE / "articles"
OUT = BASE / "docs"
OUT.mkdir(exist_ok=True)

SITE = "https://fantasticcrazyworld.github.io/tsumugi-memo"
SITE_NAME = "つむぎメモ"
SITE_DESC = "Xで話題の本・暮らしに役立つモノ・お金の知識を、毎日ウォッチして紡ぐメモ。運営: やん(@tsumugi_memo15)"

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
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{title}"><meta property="og:description" content="{desc}">
<meta property="og:type" content="article"><meta property="og:url" content="{url}">
<link rel="alternate" type="application/rss+xml" title="{site}" href="{site_url}/rss.xml">
{jsonld}<style>{css}</style></head><body>
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


def first_para(md: str) -> str:
    for line in md.split("\n")[1:]:
        line = line.strip()
        if line and not line.startswith("#"):
            plain = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line).replace("**", "")
            return plain[:110]
    return SITE_DESC[:110]


posts = []
for f in sorted(ART.glob("*.md"), reverse=True):
    md = f.read_text(encoding="utf-8")
    title = md.split("\n")[0].lstrip("# ").strip()
    date = f.stem[:10]
    slug = f.stem + ".html"
    url = f"{SITE}/{slug}"
    desc = first_para(md)
    jsonld = (
        '<script type="application/ld+json">{'
        f'"@context":"https://schema.org","@type":"Article","headline":{title!r},'
        f'"datePublished":"{date}","inLanguage":"ja",'
        f'"author":{{"@type":"Person","name":"やん","url":"https://x.com/tsumugi_memo15"}},'
        f'"publisher":{{"@type":"Organization","name":"{SITE_NAME}"}},'
        f'"description":{desc!r},"mainEntityOfPage":"{url}"'
        "}</script>"
    ).replace("'", '"')
    page = HEAD.format(title=f"{title} | {SITE_NAME}", desc=html.escape(desc),
                       url=url, jsonld=jsonld, css=CSS, site=SITE_NAME, site_url=SITE)
    page += '<div class="pr">※本記事にはプロモーション(PR)が含まれます</div>'
    page += f'<div class="date">{date}</div>' + md2html(md) + FOOT
    (OUT / slug).write_text(page, encoding="utf-8")
    posts.append((date, title, slug, desc))

# index
jsonld_site = ('<script type="application/ld+json">{"@context":"https://schema.org",'
               f'"@type":"WebSite","name":"{SITE_NAME}","url":"{SITE}/",'
               f'"description":"{SITE_DESC}","inLanguage":"ja"}}</script>')
idx = HEAD.format(title=f"{SITE_NAME} | 本と暮らしとお金の知って得したメモ", desc=SITE_DESC,
                  url=f"{SITE}/", jsonld=jsonld_site, css=CSS, site=SITE_NAME, site_url=SITE)
idx += "<h1>記事一覧</h1>"
for date, title, slug, _ in posts:
    idx += f'<p><span class="date">{date}</span><br><a href="./{slug}">{title}</a></p>'
idx += FOOT
(OUT / "index.html").write_text(idx, encoding="utf-8")

# robots.txt — AIクローラーを明示的に歓迎
(OUT / "robots.txt").write_text(
    "\n".join(f"User-agent: {b}\nAllow: /\n" for b in
              ["*", "GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-Web",
               "anthropic-ai", "PerplexityBot", "Google-Extended", "GoogleOther",
               "Applebot-Extended", "CCBot", "meta-externalagent"])
    + f"\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")

# sitemap.xml
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
sm += f"<url><loc>{SITE}/</loc></url>\n"
for date, _, slug, _ in posts:
    sm += f"<url><loc>{SITE}/{slug}</loc><lastmod>{date}</lastmod></url>\n"
(OUT / "sitemap.xml").write_text(sm + "</urlset>\n", encoding="utf-8")

# rss.xml
rss = ('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>'
       f"<title>{SITE_NAME}</title><link>{SITE}/</link><description>{SITE_DESC}</description>")
for date, title, slug, desc in posts:
    rss += (f"<item><title>{html.escape(title)}</title><link>{SITE}/{slug}</link>"
            f"<description>{html.escape(desc)}</description><pubDate>{date}</pubDate></item>")
(OUT / "rss.xml").write_text(rss + "</channel></rss>\n", encoding="utf-8")

# llms.txt — AIエージェント向けのサイト説明 (提案標準)
llms = f"# {SITE_NAME}\n\n> {SITE_DESC}\n\nXで実際に話題になっている本・商品・お金の知識を、日本語で毎日記録しているサイトです。記事には商品への参照リンク(PR)が含まれます。\n\n## 記事一覧\n\n"
for date, title, slug, desc in posts:
    llms += f"- [{title}]({SITE}/{slug}): {desc}\n"
(OUT / "llms.txt").write_text(llms, encoding="utf-8")

print(f"built {len(posts)} article(s) + robots/sitemap/rss/llms.txt -> docs/")
