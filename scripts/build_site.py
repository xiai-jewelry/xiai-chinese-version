#!/usr/bin/env python3
"""生成玺爱珠宝中文站（xiai-jewelry.cn）全部页面。

在仓库根目录运行：   python3 scripts/build_site.py
然后运行：           python3 scripts/make_font.py   （按页面用字裁剪中文宋体）

生成：index.html、products/index.html、products/<品类>.html、
products/<货号>.html、pearl-guide.html、our-story.html、wholesale.html、
contact.html、404.html 和 sitemap.xml。样式在 assets/site.css，交互在
assets/site.js，直接修改这两个文件即可。

页面上的每一件产品都来自 data/products.json（企业 SKU 信息收集表的中文文案）。
AI 生成的模特图在下方 CAMPAIGN 中登记，只用于表里真实存在的款式。
英文版在 https://xiai-jewelry.github.io ，页面结构与这里一一对应。
"""
import hashlib
import html
import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://xiai-jewelry.cn"
EN_SITE = "https://xiai-jewelry.github.io"
PHONE = "+86 135 8738 8738"
TEL = "+8613587388738"
COMPANY = "诸暨市易承珍珠养殖有限公司"
ADDRESS_ZH = "浙江省诸暨市山下湖镇云山金府2幢玺爱珠宝创意园"
BRAND = "玺爱珠宝"

e = html.escape
products = json.loads((ROOT / "data/products.json").read_text(encoding="utf-8"))
BY_SKU = {p["sku"]: p for p in products}


def ver(path):
    return hashlib.md5((ROOT / path).read_bytes()).hexdigest()[:8]


CSS_V, JS_V = ver("assets/site.css"), ver("assets/site.js")


def size(src):
    """图片宽高（用于 width/height 属性）。"""
    with Image.open(ROOT / src.lstrip("/")) as im:
        return im.size


# ---------------------------------------------------------------- data -----
# 每款所用的珍珠种类，对应 SKU 表里的珍珠栏。
PEARLS = {
    "golden": dict(name="金珠", short="金珠", img="/images/products/33187/33187-01.jpg",
                   skus="13162 13165 13210 14121 23183 33168 33187 43018 52018 53070 62021 63034 63061 73069 73081"),
    "white": dict(name="澳白珍珠", short="澳白", img="/images/products/62038/62038-01.jpg",
                  skus="14121 32089 44020 52018 62038"),
    "tahitian": dict(name="大溪地珍珠", short="大溪地", img="/images/products/34115/34115-01.jpg",
                     skus="14103 14121 14157 14164 14174 34108 34115 44020 54057 64048 64053 74021"),
    "akoya": dict(name="Akoya珍珠", short="Akoya", img="/images/products/66055/66055-01.jpg",
                  skus="14121 14164 14174 44020 66055"),
    "freshwater": dict(name="淡水珍珠", short="淡水", img="/images/products/11508/11508-01.jpg",
                       skus="11508 31335 31349"),
}
for k in PEARLS:
    PEARLS[k]["skus"] = PEARLS[k]["skus"].split()
for p in products:
    p["pearls"] = [k for k, v in PEARLS.items() if p["sku"] in v["skus"]]
    assert p["pearls"], f"no pearl type for {p['sku']}"
for k, v in PEARLS.items():
    for s in v["skus"]:
        assert s in BY_SKU, f"pearl list names unknown item {s}"

# `name` 是 products.json 里的品类键（英文），`zh` 是页面上显示的名称。
CATEGORIES = [
    dict(slug="necklaces", name="Necklaces", zh="项链", tile="/images/products/14174/14174-01.jpg",
         blurb="整串、单珠、长链与多层款式，涵盖海水与淡水珍珠。"),
    dict(slug="earrings", name="Earrings", zh="耳饰", tile="/images/products/33187/33187-01.jpg", head="/images/products/34115/34115-02.jpg",
         blurb="耳钉、耳坠与耳圈，从精致的淡水小珠到大颗金珠与大溪地珍珠。"),
    dict(slug="rings", name="Rings", zh="戒指", tile="/images/products/64048/64048-01.jpg",
         blurb="单珠、双珠与三珠戒指。每一款的戒围都会在下单前与你确认。"),
    dict(slug="bracelets", name="Bracelets", zh="手链手镯", tile="/images/products/52018/52018-01.jpg", head="/images/products/52018/52018-02.jpg",
         blurb="多层手镯与间隔式手链，搭配金珠、澳白与大溪地珍珠。"),
    dict(slug="pendants", name="Pendants", zh="吊坠", tile="/images/products/23183/23183-01.jpg", head="/images/products/23183/23183-03.jpg",
         blurb="一颗金珠吊坠，可以搭配你已有的链条。"),
    dict(slug="brooches", name="Brooches", zh="胸针", tile="/images/products/73081/73081-01.jpg", head="/images/products/73081/73081-02.jpg",
         blurb="有造型感的胸针，为外套、针织衫或围巾添一处亮点。"),
]
CAT_BY_NAME = {c["name"]: c for c in CATEGORIES}
for c in CATEGORIES:
    c["items"] = [p for p in products if p["category"] == c["name"]]
    assert c["items"], c["name"]


def kind(p):
    """产品页小标题里的品类，例如“项链”“手镯”。"""
    if p["category"] == "Bracelets":
        return "手镯" if "手镯" in p["name"] else "手链"
    return CAT_BY_NAME[p["category"]]["zh"]


# AI 生成的模特图（Canva，以实物照片为参考）。每张都必须对应真实货号；删掉一行即可停用。
CAMPAIGN = {
    "hero": dict(src="/images/campaign/hero-33168.jpg", sku="33168", pos="74% 35%"),
    "mixed": dict(src="/images/campaign/mixed-14121.jpg", sku="14121"),
    "ring": dict(src="/images/campaign/ring-63034.jpg", sku="63034"),
}
CAMPAIGN = {k: v for k, v in CAMPAIGN.items() if (ROOT / v["src"].lstrip("/")).exists()}
for v in CAMPAIGN.values():
    assert v["sku"] in BY_SKU, v
WORN = {v["sku"]: v for v in CAMPAIGN.values()}
CAT_HEAD_CAMPAIGN = {"Necklaces": "mixed", "Rings": "ring"}
AI_NOTE = "本站模特图片及部分广告图片由AI生成；产品页展示的是首饰实物照片。"

# 首页轮播（左右无边框），顺序按企业确定：三张静物图，最后是品牌影片。
# `tone`：宽屏上文字的显示方式（light：浅色蒙层上的深色字；dark：深色蒙层上的白字）；
# `pos`：文字位置，避开首饰；`narrow`：首饰占满中间时，文字收在旁边的留白里。
# 手机上文字统一放在图片下方。
SLIDES = [
    dict(img="/images/home/slide-1-pearls-on-satin.jpg", tone="light", pos="right", slogan=True,
         alt="奶油色缎面上的珍珠项链、珍珠手链与一枚金珠戒指"),
    dict(img="/images/home/slide-2-golden-earrings.jpg", tone="light", pos="right", narrow=True,
         alt="石材上的一对金珠耳饰，上方为镶石菱形耳托",
         title="金珠", text="从浅香槟色、奶油金，到浓郁的金色。",
         cta=("了解更多", "金珠", "/pearl-guide#golden")),
    dict(img="/images/home/slide-3-purple-earrings.jpg", tone="dark", pos="right", narrow=True,
         alt="深色大理石上的一对紫色珍珠耳饰，上方为闪耀的花簇耳托",
         title="淡水珍珠", text="生长在诸暨周边的湖泊里，形状、大小与颜色最为丰富。",
         cta=("了解更多", "淡水珍珠", "/pearl-guide#freshwater")),
]
SLIDES = [s for s in SLIDES if (ROOT / s["img"].lstrip("/")).exists()]

# 企业提供的品牌影片：轮播最后一页，翻到这一页才开始加载。
FILM = dict(src="/media/xiai-film.mp4", poster="/images/film-poster.jpg", title="走进玺爱",
            text="我们的展厅、工坊与秀场。", cta=("品牌故事", "/our-story"))
FILM = FILM if (ROOT / FILM["src"].lstrip("/")).exists() else None

# 首页“人物试戴”：先放企业提供的模特图，再放原来的三张模特图（链接到对应款式），最后是展厅实拍。
TRY_ON = [
    dict(img="/images/home/worn-black-dress.jpg", ai=True, cap="深色珍珠项链，配黑色晚装。",
         alt="身穿黑色V领连衣裙、佩戴深色珍珠项链的对镜自拍"),
    dict(img="/images/home/worn-grey-knit.jpg", ai=True, cap="长款，戴在灰色针织衫外。",
         alt="身穿灰色针织衫和阔腿裤、佩戴深色长款珍珠项链的女性"),
    dict(img="/images/home/worn-cluster-earrings.jpg", ai=True, cap="灰色珍珠花簇耳钉。",
         alt="灰色珍珠花簇耳钉特写"),
    dict(campaign="hero", alt="模特佩戴玺爱奶油金珠耳饰"),
    dict(campaign="mixed", alt="身穿白衬衫、佩戴多彩海水珍珠项链的模特"),
    dict(campaign="ring", alt="搭在驼色大衣上、佩戴金珠戒指的手"),
    dict(img="/images/home/showroom-14157.jpg", ai=False, sku="14157", pos="50% 45%",
         alt="玺爱展厅陈列的大溪地珍珠项链，珍珠之间以金色小珠间隔"),
]

ICON = {
    "prev": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><path d="M14.5 5.5 8 12l6.5 6.5"/></svg>',
    "next": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><path d="M9.5 5.5 16 12l-6.5 6.5"/></svg>',
    "pause": '<svg class="i-main" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><rect x="6.5" y="5" width="3.6" height="14" rx="1"/><rect x="13.9" y="5" width="3.6" height="14" rx="1"/></svg>',
    "play": '<svg class="i-alt" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 5.2v13.6L19 12z"/></svg>',
    "muted": '<svg class="i-main" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><path d="M3.5 9.5h3.8L12 5.5v13l-4.7-4H3.5z" fill="currentColor" stroke="none"/><path d="m15.5 9.5 5 5m0-5-5 5"/></svg>',
    "sound": '<svg class="i-alt" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true"><path d="M3.5 9.5h3.8L12 5.5v13l-4.7-4H3.5z" fill="currentColor" stroke="none"/><path d="M15.5 9a4.2 4.2 0 0 1 0 6M18.2 6.5a8 8 0 0 1 0 11"/></svg>',
}


def metal(p):
    """卡片上的简短材质，例如“18K金”“925银”。"""
    m = dict(p["specs"]).get("材质", "")
    for cut in ("，", "（", "("):
        m = m.split(cut)[0]
    return m.replace("配件", "")


def count(n):
    return f"{n}件"


# ------------------------------------------------------------ chrome ------
def head(title, desc, path, image, ld=(), preload=""):
    url = SITE + path
    ld_html = "\n".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    pre = f'\n<link rel="preload" href="{preload}" as="image" fetchpriority="high">' if preload else ""
    alt_lang = "" if path == "/404" else (f'\n<link rel="alternate" hreflang="zh-CN" href="{url}">'
                                          f'\n<link rel="alternate" hreflang="en" href="{EN_SITE}{path}">')
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#F8F5F0">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">{alt_lang}
<link rel="icon" type="image/png" href="/images/favicon.png">
<meta property="og:type" content="website">
<meta property="og:locale" content="zh_CN">
<meta property="og:site_name" content="{BRAND} XIAI JEWELRY">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}{image}">
<meta name="twitter:card" content="summary_large_image">
<link rel="preload" href="/fonts/xiai-serif-sc.woff2" as="font" type="font/woff2" crossorigin>{pre}
<link rel="stylesheet" href="/assets/site.css?v={CSS_V}">
{ld_html}
</head>
<body>
<a class="skip" href="#main">跳到正文</a>"""


def header(current=""):
    def cur(key):
        return ' aria-current="page"' if current == key else ""

    cats = "\n".join(f'<li><a href="/products/{c["slug"]}">{c["zh"]}</a></li>' for c in CATEGORIES)
    pearls = "\n".join(f'<li><a href="/pearl-guide#{k}">{v["name"]}</a></li>' for k, v in PEARLS.items())
    fig = ""
    if "mixed" in CAMPAIGN:
        fig = f"""<figure><img src="{CAMPAIGN['mixed']['src']}" alt="模特佩戴多彩海水珍珠项链" width="400" height="500" loading="lazy">
          <figcaption>为什么只选一种颜色？<a class="ul" href="/products/14121">查看这条项链</a></figcaption></figure>"""
    return f"""
<div class="bar">来自中国珍珠之乡诸暨山下湖，欢迎各地朋友咨询。</div>
<header class="site-header">
  <div class="wrap mast">
    <div class="mast-side">
      <button class="menu-btn" type="button" aria-controls="drawer" aria-expanded="false"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.3" aria-hidden="true"><path d="M3 7h18M3 12h18M3 17h18"/></svg>菜单</button>
    </div>
    <a class="logo" href="/" aria-label="玺爱珠宝首页"><img src="/images/logo-horizontal.png" alt="玺爱珠宝 XIAI JEWELRY" width="238" height="46"></a>
    <div class="mast-side end">
      <a class="hide-sm" href="tel:{TEL}">{PHONE}</a>
      <a class="ul" href="/contact">咨询</a>
    </div>
  </div>
  <nav class="mainnav" aria-label="主导航">
    <ul>
      <li class="has-mega{' is-current' if current == 'jewellery' else ''}">
        <button type="button" aria-expanded="false" aria-controls="mega-jewellery">珠宝</button>
        <div class="mega" id="mega-jewellery">
          <div class="wrap">
            <div><h2>珠宝</h2><ul><li><a href="/products">全部珠宝</a></li>
{cats}</ul></div>
            <div><h2>按珍珠选购</h2><ul>
{pearls}</ul></div>
            {fig}
          </div>
        </div>
      </li>
      <li><a href="/pearl-guide"{cur('guide')}>珍珠指南</a></li>
      <li><a href="/our-story"{cur('story')}>品牌故事</a></li>
      <li><a href="/wholesale"{cur('wholesale')}>批发与定制</a></li>
      <li><a href="/contact"{cur('contact')}>联系我们</a></li>
    </ul>
  </nav>
</header>
<div class="drawer" id="drawer" aria-hidden="true">
  <div class="drawer-top"><img src="/images/logo-horizontal.png" alt="玺爱珠宝" width="176" height="34"><button class="drawer-close" type="button">关闭</button></div>
  <nav aria-label="手机导航">
    <h2>珠宝</h2>
    <ul><li><a href="/products">全部珠宝</a></li>
{cats}</ul>
    <h2>玺爱</h2>
    <ul><li><a href="/pearl-guide">珍珠指南</a></li><li><a href="/our-story">品牌故事</a></li><li><a href="/wholesale">批发与定制</a></li><li><a href="/contact">联系我们</a></li></ul>
    <p class="contact-mini">电话 / 微信 <a href="tel:{TEL}">{PHONE}</a></p>
  </nav>
</div>
<main id="main">"""


def footer():
    cats = "\n".join(f'<li><a href="/products/{c["slug"]}">{c["zh"]}</a></li>' for c in CATEGORIES)
    return f"""</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="foot">
      <div class="brand">
        <img src="/images/logo-horizontal.png" alt="玺爱珠宝 XIAI JEWELRY" width="218" height="42" loading="lazy">
        <p>来自诸暨山下湖的海水与淡水珍珠首饰。自1976年起，一家人与珍珠为伴。</p>
      </div>
      <div><h2>珠宝</h2><ul><li><a href="/products">全部珠宝</a></li>
{cats}</ul></div>
      <div><h2>玺爱</h2><ul><li><a href="/pearl-guide">珍珠指南</a></li><li><a href="/our-story">品牌故事</a></li><li><a href="/wholesale">批发与定制</a></li><li><a href="/contact">联系与常见问题</a></li></ul></div>
      <div><h2>联系我们</h2><ul><li>陈先生（玺爱哥）</li><li><a href="tel:{TEL}">{PHONE}</a></li><li><a href="/contact#wechat">微信</a></li><li>中国·浙江诸暨·山下湖镇</li></ul></div>
    </div>
    <div class="legal">
      <p>XIAI JEWELRY®（玺爱珠宝）为{COMPANY}旗下品牌。{AI_NOTE}</p>
      <p>© 2026 玺爱珠宝 · <a href="{EN_SITE}/" lang="en">English</a></p>
    </div>
  </div>
</footer>
<script src="/assets/site.js?v={JS_V}" defer></script>
</body>
</html>
"""


def card(p, lazy=True):
    a, b = p["photos"][0], p["photos"][1] if len(p["photos"]) > 1 else None
    w, h = size(a)
    alt_img = f'<img class="alt" src="{b}" alt="" width="{w}" height="{h}" loading="lazy">' if b else ""
    return (f'<a class="card" href="/products/{p["sku"]}" data-pearls="{" ".join(p["pearls"])}">'
            f'<div class="ph"><img src="{a}" alt="{e(p["name"])}，货号{p["sku"]}" width="{w}" height="{h}"{" loading=\"lazy\"" if lazy else ""}>{alt_img}</div>'
            f'<h3>{e(p["name"])}</h3><p class="meta">{e(metal(p))}&ensp;&ensp;货号 {p["sku"]}</p></a>')


def grid(items, lazy=True):
    return '<div class="grid">\n' + "\n".join(card(p, lazy) for p in items) + "\n</div>"


def filters(items):
    present = [(k, v) for k, v in PEARLS.items() if any(k in p["pearls"] for p in items)]
    if len(present) < 2:
        return f'<div class="filters"><span class="note" id="shown">共 {len(items)} 件</span></div>'
    chips = "".join(
        f'<button class="chip" type="button" data-filter="{k}" aria-pressed="false">{v["short"]} <span class="n">{sum(k in p["pearls"] for p in items)}</span></button>'
        for k, v in present)
    return (f'<div class="filters" role="group" aria-label="按珍珠筛选"><span class="label">珍珠</span>'
            f'<button class="chip" type="button" data-filter="all" aria-pressed="true">全部 <span class="n">{len(items)}</span></button>{chips}'
            f'<span class="note" id="shown" aria-live="polite" style="margin-left:auto">共 {len(items)} 件</span></div>')


def wearing(key):
    c = CAMPAIGN[key]
    p = BY_SKU[c["sku"]]
    return f'<p class="wearing">模特佩戴：<a href="/products/{p["sku"]}">{e(p["name"])}</a>，货号{p["sku"]}。AI生成图片。</p>'


def crumbs(*parts):
    out = ['<a href="/">首页</a>']
    for label, href in parts:
        out.append(f'<a href="{href}">{e(label)}</a>' if href else e(label))
    return '<nav class="crumbs" aria-label="面包屑导航">' + " / ".join(out) + "</nav>"


def write(rel, text):
    out = ROOT / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print("built", rel)


# ------------------------------------------------------------- pages ------
SLOGAN = """<h1>因为玺爱，<br>所以喜爱</h1>
          <p class="sub">金珠、澳白与大溪地珍珠，在山下湖源头精挑细选，镶嵌于金与银之间。</p>
          <div class="btns"><a class="btn fill" href="/products">探索全部珠宝</a></div>"""


def hero_carousel():
    """首页顶部左右无边框的轮播（参考 xueluopearl.com）：三张静物图，最后是品牌影片。
    宽屏上铺满首屏；箭头、自动翻页、文字动效和影片按钮由 site.js 负责。"""
    if not SLIDES:  # 还没有轮播图时：标语配一张实物照片
        hp = BY_SKU["33168"]
        w, h = size(hp["photos"][0])
        return f"""<section class="hero" aria-label="品牌介绍">
  <div class="wrap"><div class="hero-split">
    <div class="hero-copy-alt">
          {SLOGAN}
    </div>
    <a class="hero-product" href="/products/{hp['sku']}"><img src="{hp['photos'][0]}" alt="{e(hp['name'])}，货号{hp['sku']}" width="{w}" height="{h}" fetchpriority="high"><span>{e(hp['name'])}，货号{hp['sku']}</span></a>
  </div></div>
</section>"""

    slides = []  # （样式类，圆点说明，内容）
    for i, s in enumerate(SLIDES):
        w, h = size(s["img"])
        pri = ' fetchpriority="high"' if i == 0 else ' fetchpriority="low" decoding="async"'
        if s.get("slogan"):
            copy = SLOGAN
        else:
            label, more, href = s["cta"]  # 按钮上显示短词，读屏软件会读出完整说明
            copy = (f'<h2>{e(s["title"])}</h2>\n          <p>{e(s["text"])}</p>\n'
                    f'          <div class="btns"><a class="btn fill" href="{href}">{e(label)}<span class="vh">：{e(more)}</span></a></div>')
        cls = f"t-{s['tone']} p-{s['pos']}" + (" c-narrow" if s.get("narrow") else "")
        slides.append((cls, s.get("title", "珠宝系列"), f"""<img src="{s['img']}" alt="{e(s['alt'])}" width="{w}" height="{h}"{pri}>
        <div class="slide-copy">
          {copy}
        </div>"""))
    if FILM:
        src = f'{FILM["src"]}?v={ver(FILM["src"].lstrip("/"))}'
        label, href = FILM["cta"]
        slides.append(("s-film t-dark p-left", FILM["title"], f"""<video id="film" muted loop playsinline controls preload="none" poster="{FILM['poster']}" aria-label="玺爱珠宝品牌影片">
          <source src="{src}" type="video/mp4">
        </video>
        <div class="slide-copy">
          <h2>{e(FILM['title'])}</h2>
          <p>{e(FILM['text'])}</p>
          <div class="btns"><a class="btn fill" href="{href}">{e(label)}</a></div>
        </div>
        <div class="film-ctrl">
          <button class="film-play" type="button" aria-label="播放影片">{ICON['pause']}{ICON['play']}</button>
          <button class="film-sound" type="button" aria-label="打开声音">{ICON['muted']}{ICON['sound']}</button>
        </div>"""))
    n = len(slides)
    items = "\n".join(
        f"""    <div class="slide {cls}" role="group" aria-roledescription="幻灯片" aria-label="第{i + 1}张，共{n}张">
      <div class="slide-frame">
        {inner}
      </div>
    </div>""" for i, (cls, label, inner) in enumerate(slides))
    arrows = dots = ""
    if n > 1:  # 箭头放在前面，键盘用户先到达箭头
        arrows = f"""
    <button class="car-btn prev" type="button" aria-controls="hero-track" aria-label="上一张">{ICON['prev']}</button>
    <button class="car-btn next" type="button" aria-controls="hero-track" aria-label="下一张">{ICON['next']}</button>"""
        dots = "\n    <div class=\"car-dots\">" + "".join(
            f'<button type="button" aria-controls="hero-track" aria-label="第{i + 1}张：{e(label)}"'
            f'{" aria-current=\"true\"" if i == 0 else ""}></button>' for i, (cls, label, inner) in enumerate(slides)) + "</div>"
    return f"""<section class="hero" aria-roledescription="轮播" aria-label="精选">
  <div class="car" data-carousel>{arrows}
    <div class="car-track" id="hero-track">
{items}
    </div>{dots}
  </div>
</section>"""


def try_on():
    """“人物试戴”：模特图与展厅实拍，可左右滑动，宽屏有箭头。已知款式的说明会链接到产品页。"""
    looks, any_ai = [], False
    for t in TRY_ON:
        if "campaign" in t:
            if t["campaign"] not in CAMPAIGN:
                continue
            c = CAMPAIGN[t["campaign"]]
            src, sku, ai, pos = c["src"], c["sku"], True, c.get("pos")
            cap = None
        else:
            src, sku, ai, pos, cap = t["img"], t.get("sku"), t["ai"], t.get("pos"), t.get("cap")
            if not (ROOT / src.lstrip("/")).exists():
                continue
        any_ai = any_ai or ai
        w, h = size(src)
        if sku:
            p = BY_SKU[sku]
            text = ("" if ai else "展厅实拍：") + f'<a href="/products/{sku}">{e(p["name"])}</a>，货号{sku}。'
        else:
            text = e(cap)
        style = f' style="object-position:{pos}"' if pos else ""
        looks.append(f'<figure class="look"><img src="{src}" alt="{e(t["alt"])}" width="{w}" height="{h}" loading="lazy"{style}>'
                     f'<figcaption>{text}</figcaption></figure>')
    if not looks:
        return ""
    note = '\n    <p class="note look-note">模特图片由AI生成。</p>' if any_ai else ""
    return f"""<section class="sec" aria-labelledby="worn-h">
  <div class="wrap">
    <div class="head"><h2 id="worn-h">人物试戴</h2><p>日常与晚宴都适合的珍珠，从小黑裙到休闲的灰色针织衫。</p></div>
    <div class="strip-box" data-strip>
      <button class="strip-btn prev" type="button" aria-controls="worn-strip" aria-label="上一组图片">{ICON['prev']}</button>
      <button class="strip-btn next" type="button" aria-controls="worn-strip" aria-label="更多图片">{ICON['next']}</button>
      <div class="strip" id="worn-strip" role="region" aria-label="人物试戴图片" tabindex="0">
        {"".join(looks)}
      </div>
    </div>{note}
  </div>
</section>"""


def home():
    edit = [BY_SKU[s] for s in "33187 34115 14174 52018 64048 73081 32089 13210".split()]
    tiles = "\n".join(
        f'<a class="tile" href="/products/{c["slug"]}"><img src="{c["tile"]}" alt="" width="1400" height="1400" loading="lazy"><span>{c["zh"]}<small>{count(len(c["items"]))}</small></span></a>'
        for c in CATEGORIES)
    pearls = "\n".join(
        f'<a href="/pearl-guide#{k}"><img src="{v["img"]}" alt="" width="400" height="400" loading="lazy"><b>{v["name"]}</b><span>{count(len(v["skus"]))}</span></a>'
        for k, v in PEARLS.items())

    ld = [{
        "@context": "https://schema.org", "@type": "JewelryStore", "@id": SITE + "/#store",
        "name": BRAND, "alternateName": ["XIAI JEWELRY", "Xiai Jewelry"],
        "slogan": "因为玺爱，所以喜爱",
        "url": SITE + "/", "logo": SITE + "/images/logo-vertical.png", "image": SITE + "/images/showroom.jpg",
        "description": "位于诸暨山下湖的珍珠首饰品牌，提供金珠、澳白、大溪地、Akoya与淡水珍珠的项链、耳饰、戒指、手链手镯、吊坠与胸针，并承接批发与定制。",
        "telephone": PHONE, "inLanguage": "zh-CN",
        "address": {"@type": "PostalAddress", "streetAddress": "云山金府2幢玺爱珠宝创意园",
                    "addressLocality": "诸暨市山下湖镇", "addressRegion": "浙江省", "addressCountry": "CN"},
        "parentOrganization": {"@type": "Organization", "name": COMPANY, "alternateName": "Zhuji Yicheng Pearl Farming Co., Ltd."},
        "foundingDate": "2010",
        "memberOf": {"@type": "Organization", "name": "浙江省珍珠行业协会"},
    }]
    og = SLIDES[0]["img"] if SLIDES else CAMPAIGN["hero"]["src"] if "hero" in CAMPAIGN else edit[0]["photos"][0]
    body = f"""{hero_carousel()}
<section class="sec" aria-labelledby="edit-h">
  <div class="wrap">
    <div class="head"><h2 id="edit-h">精选</h2><p>先从这几件开始。每一件都有自己的页面，附实物照片与详细介绍。</p></div>
    {grid(edit)}
    <div class="after"><a class="btn" href="/products">查看全部{len(products)}件</a></div>
  </div>
</section>
{try_on()}
<section class="band" aria-labelledby="find-h">
  <div class="wrap">
    <div class="head"><h2 id="find-h">找到你的珍珠</h2><p>从日常耳钉，到醒目的戒指与胸针。</p></div>
    <div class="tiles">
{tiles}
    </div>
  </div>
</section>
<section class="sec" aria-labelledby="types-h">
  <div class="wrap">
    <div class="head"><h2 id="types-h">认识珍珠</h2><p>以海水珍珠为主，也有淡水珍珠。先了解每种珍珠的不同，再看用它做成的作品。</p></div>
    <div class="pearls">
{pearls}
    </div>
    <div class="after"><a class="btn" href="/pearl-guide">阅读珍珠指南</a></div>
  </div>
</section>
<section class="split plain" aria-labelledby="roots-h">
  <div class="media"><img src="/images/farm-lake.jpg" alt="诸暨附近湖面上的珍珠养殖场" width="1800" height="1200" loading="lazy"></div>
  <div class="copy">
    <h2 id="roots-h">1976年起，扎根山下湖</h2>
    <p>我们一家从1976年开始与珍珠打交道。如今，玺爱立足山下湖珍珠产业带，紧邻养殖、采收、分级与原珠供应，并在诸暨设有展厅。</p>
    <div class="btns"><a class="btn" href="/our-story">品牌故事</a></div>
  </div>
</section>
<section class="sec oat" aria-labelledby="trade-h">
  <div class="wrap trade">
    <div>
      <h2 id="trade-h">面向零售商、主播与定制客户</h2>
      <ul>
        <li><b>批发与渠道供货</b><span>稳定货源、选品支持与可靠交付。</span></li>
        <li><b>直播合作</b><span>为主播选品，并提供现场直播支持。</span></li>
        <li><b>定制</b><span>按需挑选珍珠，按你的要求设计。</span></li>
      </ul>
      <a class="btn fill" href="/wholesale">与我们合作</a>
    </div>
    <img src="/images/display.jpg" alt="玺爱展厅里一盘盘珍珠首饰" width="1200" height="675" loading="lazy">
  </div>
</section>
<section class="sec" aria-label="服务">
  <div class="wrap services">
    <div><h3>咨询任意款式</h3><p>告诉我们货号，我们可以提供更多照片或视频、尺寸与价格。</p><a class="ul" href="/contact">联系我们</a></div>
    <div><h3>按需定制</h3><p>按需挑选珍珠，按你的要求设计。费用与交期逐单确认。</p><a class="ul" href="/wholesale#custom">定制服务</a></div>
    <div><h3>参观展厅</h3><p>到诸暨山下湖的玺爱珠宝创意园，现场看、现场挑。</p><a class="ul" href="/our-story#showroom">展厅介绍</a></div>
    <div><h3>证书</h3><p>购买前，我们会确认这件作品附带哪种证书，以及适用的售后条款。</p><a class="ul" href="/contact#faq">常见问题</a></div>
  </div>
</section>"""
    return (head("玺爱珠宝 XIAI JEWELRY · 山下湖金珠、大溪地与南洋珍珠首饰",
                 "来自诸暨山下湖的珍珠首饰：金珠、澳白、大溪地、Akoya与淡水珍珠项链、耳饰、戒指、手链手镯与胸针。欢迎各地咨询。",
                 "/", og, ld, preload=SLIDES[0]["img"] if SLIDES else "") + header("home") + body + footer())


def listing(cat=None):
    items = cat["items"] if cat else products
    chips = "".join(
        f'<a class="chip" href="/products/{c["slug"]}"{" aria-current=\"page\"" if cat and c is cat else ""}>{c["zh"]} <span class="n">{len(c["items"])}</span></a>'
        for c in CATEGORIES)
    allchip = f'<a class="chip" href="/products"{"" if cat else " aria-current=\"page\""}>全部 <span class="n">{len(products)}</span></a>'
    if cat:
        key = CAT_HEAD_CAMPAIGN.get(cat["name"])
        if key in CAMPAIGN:
            img, alt, note = CAMPAIGN[key]["src"], f"玺爱{cat['zh']}，上身效果", wearing(key)
        else:
            img, alt, note = cat.get("head", cat["tile"]), f"玺爱{cat['zh']}", ""
        w, h = size(img)
        top = f"""<div class="wrap">
  {crumbs(('珠宝', '/products'), (cat['zh'], None))}
  <div class="cat-head">
    <div><h1>{cat['zh']}</h1><p class="sub">{e(cat['blurb'])}</p><p class="count">共{len(items)}件。价格、尺寸与库存，咨询时确认。</p></div>
    <figure><img src="{img}" alt="{e(alt)}" width="{w}" height="{h}" fetchpriority="high">{note}</figure>
  </div>
</div>"""
        title = f"珍珠{cat['zh']} · {BRAND}"
        desc = f"玺爱珍珠{cat['zh']}：{cat['blurb']}"
        path = f"/products/{cat['slug']}"
    else:
        top = f"""<div class="wrap">
  {crumbs(('珠宝', None))}
  <div class="page-head"><h1>全部珠宝</h1><p class="sub">{len(products)}件作品，涵盖金珠、澳白、大溪地、Akoya与淡水珍珠。价格、尺寸与库存，咨询时确认。</p></div>
</div>"""
        title, path = f"全部珍珠首饰 · {BRAND}", "/products"
        desc = f"玺爱全部{len(products)}件作品：来自诸暨山下湖的珍珠项链、耳饰、戒指、手链手镯、吊坠与胸针。"
    ld = [{"@context": "https://schema.org", "@type": "ItemList", "name": title,
           "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": f"{SITE}/products/{p['sku']}", "name": p["name"]} for i, p in enumerate(items)]}]
    body = f"""{top}
<section class="wrap" style="padding-bottom:112px" aria-label="作品">
  <nav class="filters" aria-label="品类" style="border-bottom:0;margin-bottom:0;padding-bottom:0">{allchip}{chips}</nav>
  {filters(items)}
  {grid(items, lazy=False)}
</section>"""
    return head(title, desc, path, items[0]["photos"][0], ld) + header("jewellery") + body + footer()


def product(p):
    sku, name, photos = p["sku"], p["name"], p["photos"]
    cat = CAT_BY_NAME[p["category"]]
    w, h = size(photos[0])
    alt = lambda i: f"{name}（玺爱 {sku}），第{i + 1}张，共{len(photos)}张"
    thumbs = "\n".join(
        f'<button type="button" data-src="{src}" data-alt="{e(alt(i))}" aria-label="查看第{i + 1}张照片"'
        f'{" aria-current=\"true\"" if i == 0 else ""}><img src="{src}" alt="" width="{w}" height="{h}" loading="lazy"></button>'
        for i, src in enumerate(photos))
    specs = "\n".join(f"<dt>{e(k)}</dt><dd>{e(v)}</dd>" for k, v in p["specs"])
    points = "\n".join(f"<li>{e(t)}</li>" for t in p["points"])
    faq = "\n".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in p["faq"])
    same = [o for o in products if o["sku"] != sku and o["category"] == p["category"]]
    rest = [o for o in products if o["sku"] != sku and o["category"] != p["category"] and set(o["pearls"]) & set(p["pearls"])]
    others = (same + rest)[:4]
    worn = ""
    if sku in WORN:
        worn = f"""<section class="sec tight" aria-labelledby="worn-h">
  <div class="wrap worn">
    <img src="{WORN[sku]['src']}" alt="模特佩戴{e(name)}" width="{size(WORN[sku]['src'])[0]}" height="{size(WORN[sku]['src'])[1]}" loading="lazy"{f' style="object-position:{WORN[sku]["pos"]}"' if WORN[sku].get("pos") else ""}>
    <div><h2 id="worn-h">上身效果</h2><p>{e(p['for'])}</p><p class="ai">AI生成图片，依据本款实物照片制作；上方照片为实物拍摄。</p></div>
  </div>
</section>"""
    pearl_links = "、".join(f'<a href="/pearl-guide#{k}">{PEARLS[k]["name"]}</a>' for k in p["pearls"])
    ld = [
        {"@context": "https://schema.org", "@type": "Product", "name": name, "alternateName": p["name_en"], "sku": sku,
         "category": cat["zh"], "description": p["description"], "image": [SITE + s for s in photos],
         "brand": {"@type": "Brand", "name": BRAND},
         "manufacturer": {"@type": "Organization", "name": COMPANY}, "url": f"{SITE}/products/{sku}"},
        {"@context": "https://schema.org", "@type": "FAQPage",
         "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "首页", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": cat["zh"], "item": f"{SITE}/products/{cat['slug']}"},
            {"@type": "ListItem", "position": 3, "name": name, "item": f"{SITE}/products/{sku}"}]},
    ]
    body = f"""<div class="wrap">
  {crumbs(('珠宝', '/products'), (cat['zh'], f"/products/{cat['slug']}"), (name, None))}
  <div class="pd">
    <div class="gal">
      <img class="gal-main" id="gal-main" src="{photos[0]}" alt="{e(alt(0))}" width="{w}" height="{h}" fetchpriority="high">
      <div class="thumbs">
{thumbs}
      </div>
    </div>
    <div class="info">
      <p class="kicker">{kind(p)}　货号 {sku}</p>
      <h1>{e(name)}</h1>
      <p class="zh" lang="en">{e(p['name_en'])}</p>
      <p class="tagline">{e(p['tagline'])}</p>
      <p class="desc">{e(p['description'])}</p>
      <dl class="specs">
{specs}
      </dl>
      <div class="btns"><a class="btn fill" href="/contact?item={sku}">咨询这件作品</a><a class="btn" href="tel:{TEL}">致电 {PHONE}</a></div>
      <p class="note">联系时请告知货号 {sku}。尺寸、库存与价格会在每次咨询时确认。所用珍珠：{pearl_links}。</p>
    </div>
  </div>
</div>
{worn}
<section class="sec tight oat" aria-labelledby="details-h">
  <div class="wrap">
    <div class="head" style="margin-bottom:40px"><h2 id="details-h">细节</h2></div>
    <ul class="points">
{points}
    </ul>
    {'' if sku in WORN else f'<p class="for">{e(p["for"])}</p>'}
  </div>
</section>
<section class="sec tight" aria-labelledby="faq-h">
  <div class="wrap">
    <div class="head" style="margin-bottom:36px"><h2 id="faq-h">关于货号 {sku}</h2></div>
    <div class="faq">
{faq}
    </div>
  </div>
</section>
<section class="sec tight" aria-labelledby="more-h" style="padding-top:0">
  <div class="wrap">
    <div class="head" style="margin-bottom:40px"><h2 id="more-h">你可能也喜欢</h2></div>
    {grid(others)}
    <div class="after"><a class="btn" href="/products/{cat['slug']}">全部{cat['zh']}</a></div>
  </div>
</section>"""
    title = f"{name} · 货号{sku} · {BRAND}"
    return head(title, p["description"], f"/products/{sku}", photos[0], ld) + header("jewellery") + body + footer()


GUIDE = {
    "golden": ("金珠产自大型白蝶贝（Pinctada maxima）中的金唇品种，和澳白出自同一种贝。颜色从浅香槟、奶油色一直到浓郁的金色。",
               ["我们作品中的金珠：奶油金到浓金", "我们作品中的尺寸：8–15mm", "依款式镶嵌于18K金、14K金、925银或铜合金"]),
    "white": ("澳白（白色南洋珍珠）产自银唇白蝶贝（Pinctada maxima），是体型最大的养殖珍珠之一，银白色调，光泽柔和如缎。",
              ["我们作品中的澳白：白色，包括水滴形", "我们作品中的尺寸：8–13mm", "可单独呈现，也与金珠、大溪地珍珠搭配"]),
    "tahitian": ("大溪地珍珠产自黑唇珠母贝（Pinctada margaritifera），天然颜色从银灰、铂金灰到近黑色，常带绿、蓝或玫瑰色伴色。",
                 ["我们作品中的大溪地珍珠：铂金灰与更深的灰色，包括巴洛克形", "我们作品中的尺寸：8–14mm", "很好搭配黑、白、灰与牛仔"]),
    "akoya": ("Akoya珍珠产自体型较小的马氏珠母贝（Pinctada fucata），比南洋珠和大溪地珍珠小，通常为圆形，光泽明亮如镜。",
              ["我们作品中的Akoya：白色与灰色调", "我们作品中的尺寸：3–8.5mm", "用作大珠之间的点缀，或在戒指上三颗并排"]),
    "freshwater": ("淡水珍珠生长在湖泊与池塘的河蚌中，包括玺爱所在的诸暨周边。它们的形状、大小与颜色最为丰富。",
                   ["我们作品中的淡水珍珠：白色与紫色", "我们作品中的尺寸：3–10mm", "我们也提供高品质淡水珍珠、爱迪生珍珠与淡水巴洛克珍珠，库存请咨询"]),
}


def guide():
    nav = "".join(f'<a class="chip" href="#{k}">{v["short"]}</a>' for k, v in PEARLS.items()) + '<a class="chip" href="#mabe">马贝与巴洛克</a>'
    secs = []
    for k, v in PEARLS.items():
        text, facts = GUIDE[k]
        items = [BY_SKU[s] for s in v["skus"]]
        fl = "".join(f"<li>{e(f)}</li>" for f in facts)
        secs.append(f"""<section class="pearl-sec" id="{k}" aria-labelledby="{k}-h">
  <div class="wrap">
    <div class="cols"><div><h2 id="{k}-h">{v['name']}</h2><p class="body-text" style="margin-top:18px">{e(text)}</p></div><ul class="facts">{fl}</ul></div>
    {grid(items)}
  </div>
</section>""")
    mabe = f"""<section class="pearl-sec" id="mabe" aria-labelledby="mabe-h">
  <div class="wrap cols">
    <div><h2 id="mabe-h">马贝珍珠与巴洛克珍珠</h2>
      <p class="body-text" style="margin-top:18px">马贝珍珠贴着贝壳内壁养殖而成，呈半球形、背面平整。巴洛克珍珠形状不规则，每一颗都不一样。</p>
      <p class="body-text" style="margin-top:16px">我们的巴洛克作品是<a href="/products/14103">大溪地巴洛克项链</a>。图中这类马贝珍珠作品（如鸡尾酒戒指），请向我们咨询目前的库存。</p>
      <div class="btns" style="margin-top:28px"><a class="btn" href="/contact">咨询马贝珍珠作品</a></div></div>
    <figure><img src="/images/sig-mabe-ring.jpg" alt="镶密钉光环的马贝珍珠鸡尾酒戒指" width="1200" height="1200" loading="lazy"><figcaption class="note" style="margin-top:10px">马贝珍珠鸡尾酒戒指，摄于展厅。</figcaption></figure>
  </div>
</section>"""
    body = f"""<div class="wrap">
  {crumbs(('珍珠指南', None))}
  <div class="cols" style="padding:40px 0 64px;align-items:center">
    <div class="page-head" style="padding:0"><h1>珍珠指南</h1><p class="sub">金珠、澳白、大溪地、Akoya与淡水珍珠：它们来自哪里、是什么样子，以及我们用它们做成的作品。</p>
      <nav class="guide-nav" aria-label="珍珠种类">{nav}</nav></div>
    <figure><img src="/images/pearl-types.jpg" alt="展厅里的珍珠样品盒，对比大溪地、Akoya、澳白与金珠" width="1200" height="1599" style="max-height:620px;width:auto;margin:0 auto" fetchpriority="high"><figcaption class="note center" style="margin-top:10px">展厅里的珍珠样品盒。</figcaption></figure>
  </div>
</div>
{''.join(secs)}
{mabe}"""
    return head(f"珍珠指南：金珠、南洋珠、大溪地、Akoya与淡水珍珠 · {BRAND}",
                "金珠、澳白、大溪地、Akoya、淡水、马贝与巴洛克珍珠有什么不同，以及玺爱用它们做成的作品。",
                "/pearl-guide", "/images/pearl-types.jpg") + header("guide") + body + footer()


MILESTONES = [("1976", "家族开始从事珍珠行业。"), ("1979", "第一批珍珠推向市场。"),
              ("1999", "第二代接手家族生意。"), ("2008", "入驻华东国际珠宝城。"),
              ("2010", "注册“玺爱”品牌。"), ("2012", "开始电商销售。"),
              ("2020", "转向直播电商。"), ("2021–22", "拓展主播合作，入驻抖音与微信视频号。"),
              ("2023至今", "完善供应链与合作服务。")]


def story():
    tl = "".join(f"<li><b>{y}</b><span>{e(t)}</span></li>" for y, t in MILESTONES)
    body = f"""<div class="wrap">
  {crumbs(('品牌故事', None))}
  <div class="page-head"><h1>自1976年，一家人与珍珠为伴</h1><p class="sub">玺爱位于中国珍珠之乡——浙江诸暨山下湖镇。</p></div>
  <img class="wide-img" src="/images/farm-lake.jpg" alt="诸暨附近湖面上的珍珠养殖场" width="1800" height="1200" fetchpriority="high">
</div>
<section class="sec" aria-labelledby="who-h">
  <div class="wrap cols">
    <h2 id="who-h" class="lede">依托当地的珍珠资源，我们选珠、开发设计、制作并销售珍珠首饰。</h2>
    <div class="body-text">
      <p>我们的展厅、网店与一对一顾问服务面向各类客户；选品、制作、质检、包装、发货与售后团队在每一笔订单背后协同工作。</p>
      <p>除零售客户外，我们也为销售渠道供货，并与直播主播及定制项目合作。</p>
    </div>
  </div>
</section>
<section class="sec oat" aria-labelledby="ms-h">
  <div class="wrap cols">
    <div><h2 id="ms-h" style="font-size:clamp(24px,2.4vw,34px)">大事记</h2><p class="body-text" style="margin-top:16px">两代人，从第一批珍珠推向市场，到今天的展厅与合作伙伴。</p></div>
    <ol class="timeline">{tl}</ol>
  </div>
</section>
<section class="sec" aria-labelledby="src-h">
  <div class="wrap">
    <div class="head"><h2 id="src-h">靠近珍珠旅程的每一步</h2><p>立足山下湖珍珠产业带，让我们紧邻养殖、采收、分级与原珠供应。</p></div>
    <ol class="steps">
      <li><img src="/images/farm-lake.jpg" alt="" width="1800" height="1200" loading="lazy"><h3>养殖</h3><p>珍珠在诸暨周边湖泊与池塘的河蚌中生长。</p></li>
      <li><img src="/images/opening-mussels.jpg" alt="" width="1200" height="800" loading="lazy"><h3>采收</h3><p>手工开蚌，取出珍珠。</p></li>
      <li><img src="/images/measuring.jpg" alt="" width="1200" height="800" loading="lazy"><h3>测量</h3><p>逐颗测量尺寸，让项链与耳饰配得整齐。</p></li>
      <li><img src="/images/sorting.jpg" alt="" width="1200" height="800" loading="lazy"><h3>分级</h3><p>按颜色、形状与品质分拣，分级入库。</p></li>
    </ol>
  </div>
</section>
<section class="sec oat" aria-labelledby="make-h">
  <div class="wrap">
    <div class="head"><h2 id="make-h">从需求到成品</h2><p>每一款新设计都经过同样的五个步骤，确保满足要求、进度清晰。</p></div>
    <ol class="steps five">
      <li><h3>需求</h3><p>确认款式、数量与产品要求。</p></li>
      <li><h3>设计</h3><p>围绕珍珠的特点形成初步方案。</p></li>
      <li><h3>配珠</h3><p>按尺寸、颜色与品质挑选珍珠。</p></li>
      <li><h3>打样与制作</h3><p>打孔、镶嵌、组装，完成首件样品。</p></li>
      <li><h3>终检</h3><p>检查结构、佩戴感与整体品质。</p></li>
    </ol>
  </div>
</section>
<section class="sec" id="showroom" aria-labelledby="room-h">
  <div class="wrap">
    <div class="head"><h2 id="room-h">山下湖的实体展厅</h2><p>在这里接待来访客人、洽谈项目、现场选款，也在这里拍摄内容。</p></div>
    <div class="gallery">
      <figure><img src="/images/showroom.jpg" alt="玺爱展厅与展示柜台" width="1800" height="1350" loading="lazy"><figcaption>展厅</figcaption></figure>
      <figure><img src="/images/display.jpg" alt="供现场挑选的珍珠首饰托盘" width="1200" height="675" loading="lazy"><figcaption>现场选款</figcaption></figure>
      <figure><img src="/images/studio.jpg" alt="拍摄与直播间" width="1200" height="675" loading="lazy"><figcaption>拍摄与直播间</figcaption></figure>
    </div>
  </div>
</section>
<section class="sec" style="padding-top:0" aria-labelledby="val-h">
  <div class="wrap">
    <h2 id="val-h" class="vh">我们看重的</h2>
    <div class="values">
      <div><h3>品质</h3><p>选珠与制作都坚持高标准。</p></div>
      <div><h3>审美</h3><p>让珍珠文化与现代设计、当下的穿搭相结合。</p></div>
      <div><h3>服务</h3><p>购买前给出清楚的建议，订单全程跟进，提供售后支持。</p></div>
      <div><h3>长期合作</h3><p>重视与客户和合作伙伴的长期关系。</p></div>
    </div>
  </div>
</section>
<section class="sec oat" aria-labelledby="cred-h">
  <div class="wrap">
    <div class="head"><h2 id="cred-h">行业会员与企业信用</h2></div>
    <div class="certs">
      <figure><img src="/images/cert-association.jpg" alt="牌匾：浙江省珍珠行业协会理事单位" loading="lazy"><figcaption>浙江省珍珠行业协会理事单位</figcaption></figure>
      <figure><img src="/images/cert-aaa.jpg" alt="证书：AAA级企业信用等级" loading="lazy"><figcaption>AAA级企业信用等级</figcaption></figure>
      <figure><img src="/images/cert-contract.jpg" alt="牌匾：浙江省A级“守合同重信用”企业" loading="lazy"><figcaption>浙江省A级“守合同重信用”企业</figcaption></figure>
    </div>
  </div>
</section>"""
    return head(f"品牌故事 · 自1976年扎根山下湖的珍珠世家 · {BRAND}",
                "玺爱是诸暨山下湖的珍珠世家，始于1976年：发展历程、珍珠来源、新品开发流程、展厅与企业资质。",
                "/our-story", "/images/farm-lake.jpg") + header("story") + body + footer()


def wholesale():
    body = f"""<div class="wrap">
  {crumbs(('批发与定制', None))}
  <div class="cols" style="padding:40px 0 72px;align-items:center">
    <div class="page-head" style="padding:0"><h1>批发、合作与定制</h1><p class="sub">面向零售商、品牌、主播，以及任何想要定制首饰的你。</p>
      <div class="btns" style="margin-top:30px"><a class="btn fill" href="/contact">洽谈合作</a><a class="btn" href="tel:{TEL}">致电 {PHONE}</a></div></div>
    <img src="/images/studio.jpg" alt="玺爱拍摄与直播间" width="1200" height="675" fetchpriority="high">
  </div>
</div>
<section class="sec oat" aria-labelledby="ways-h">
  <div class="wrap">
    <div class="head"><h2 id="ways-h">与玺爱合作的四种方式</h2></div>
    <ul class="ways">
      <li><h3>批发与渠道供货</h3><p>稳定货源、选品支持，为你的渠道可靠交付。</p></li>
      <li><h3>直播合作</h3><p>为主播选品，提供现场直播支持，售后由我们处理。</p></li>
      <li><h3>内容电商</h3><p>支持内容制作、店铺运营与订单履约。</p></li>
      <li id="custom"><h3>定制</h3><p>按需挑选珍珠，按你的要求设计。</p></li>
    </ul>
  </div>
</section>
<section class="sec" aria-labelledby="how-h">
  <div class="wrap">
    <div class="head"><h2 id="how-h">合作流程</h2></div>
    <div class="paths">
      <div><h3>为自己购买</h3><ol><li>浏览我们的珠宝</li><li>咨询款式与规格</li><li>确认价格与购买方式</li><li>下单后，我们安排发货</li><li>有任何售后问题，随时联系我们</li></ol></div>
      <div><h3>定制与合作</h3><ol><li>告诉我们你的需求</li><li>确认选珠与设计</li><li>确认样品或产品</li><li>交付</li></ol></div>
    </div>
  </div>
</section>
<section class="sec oat" aria-labelledby="teams-h">
  <div class="wrap cols">
    <div><h2 id="teams-h" style="font-size:clamp(24px,2.4vw,34px)">五个团队，服务每一笔订单</h2><p class="body-text" style="margin-top:16px">从选款到交付，每一个需求都有专门的团队跟进。</p>
      <img src="/images/packing.jpg" alt="在仓库里检查并打包订单" width="900" height="1125" loading="lazy" style="margin-top:36px;max-width:420px;width:100%"></div>
    <ul class="teams">
      <li><b>选品团队</b><span>款式、库存与产品信息</span></li>
      <li><b>运营与内容</b><span>渠道运营、内容策划与素材</span></li>
      <li><b>拍摄与直播</b><span>产品拍摄、直播场景与现场支持</span></li>
      <li><b>客服与订单</b><span>咨询、订单细节与进度更新</span></li>
      <li><b>仓储与物流</b><span>库存、质检、包装与物流</span></li>
    </ul>
  </div>
</section>
<section class="sec" aria-labelledby="src2-h">
  <div class="wrap">
    <div class="head"><h2 id="src2-h">靠近源头</h2><p>立足山下湖珍珠产业带，让我们紧邻养殖、采收、分级与原珠供应。</p><div class="btns"><a class="btn" href="/our-story">品牌故事</a><a class="btn" href="/products">查看作品</a></div></div>
    <div class="gallery">
      <figure><img src="/images/sorting.jpg" alt="团队手工分拣珍珠" width="1200" height="800" loading="lazy"><figcaption>分级与分拣</figcaption></figure>
      <figure><img src="/images/drilling.jpg" alt="精密机器为珍珠打孔" width="1200" height="800" loading="lazy"><figcaption>打孔</figcaption></figure>
      <figure><img src="/images/quality-check.jpg" alt="手持检查完成的珍珠手链" width="1200" height="1600" loading="lazy" style="object-position:50% 40%"><figcaption>成品检查</figcaption></figure>
    </div>
  </div>
</section>"""
    return head(f"批发、直播合作与珍珠首饰定制 · {BRAND}",
                "与玺爱合作：批发与渠道供货、直播合作、内容电商，以及来自诸暨山下湖的珍珠首饰定制。",
                "/wholesale", "/images/studio.jpg") + header("wholesale") + body + footer()


FAQ = [("玺爱卖什么？", "珍珠项链、耳饰、戒指、手链手镯、吊坠与胸针。"),
       ("你们只卖淡水珍珠吗？", "不是。我们以海水珍珠为主——南洋金珠、澳白、大溪地、Akoya与马贝珍珠——也提供高品质淡水珍珠、爱迪生珍珠与巴洛克珍珠。"),
       ("所有款式都是18K金吗？", "视款式而定，每件作品的材质都写在它的产品介绍里。"),
       ("挑选珍珠首饰时要看什么？", "款式、珍珠种类、表面品质、尺寸、镶嵌金属、实物照片和价格。任何款式我们都可以提供更多照片或视频。"),
       ("可以定制或批发吗？", "可以。告诉我们你的需求，费用与交期逐单确认。"),
       ("证书和售后怎么处理？", "购买前，我们会确认这件作品附带哪种证书，以及适用的售后条款。"),
       ("模特照片是真人吗？", "模特图片由AI依据我们的实物照片生成。每个产品页都展示了首饰的实物照片。"),
       ("怎么联系你们？", f"致电或添加陈先生微信：{PHONE}，也欢迎到诸暨山下湖的展厅参观。")]


def contact():
    names = json.dumps({p["sku"]: p["name"] for p in products}, ensure_ascii=False)
    faq = "\n".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in FAQ)
    ld = [{"@context": "https://schema.org", "@type": "FAQPage",
           "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}]
    body = f"""<div class="wrap">
  {crumbs(('联系我们', None))}
  <div class="page-head"><h1>欢迎来山下湖，或直接联系我们</h1><p class="sub">咨询任意款式、预约参观展厅，或洽谈批发、定制设计与直播合作。</p></div>
  <div class="contact-grid" style="padding-bottom:112px">
    <div>
      <p class="asking" id="asking" data-names="{e(names)}">你正在咨询 <b></b>。致电或发消息时，请告知这个货号。</p>
      <dl class="contact-list">
        <dt>联系人</dt><dd>陈先生（玺爱哥）</dd>
        <dt>电话</dt><dd><a href="tel:{TEL}">{PHONE}</a></dd>
        <dt>微信</dt><dd>扫描二维码，或搜索 {PHONE.replace(" ", "\u00a0")}</dd>
        <dt>地址</dt><dd>{ADDRESS_ZH}</dd>
      </dl>
      <img src="/images/building.jpg" alt="玺爱珠宝创意园大楼" width="1400" height="934" loading="lazy" style="margin-top:40px">
    </div>
    <div class="qr" id="wechat">
      <img src="/images/wechat-qr.jpg" alt="玺爱珠宝微信二维码" width="220" height="220" loading="lazy">
      <h2>微信咨询</h2>
      <p>用微信扫一扫，给我们发消息、发你想找的款式照片，或聊聊你的合作想法。</p>
      <a class="btn fill" href="tel:{TEL}">致电 {PHONE}</a>
    </div>
  </div>
</div>
<section class="sec oat" id="faq" aria-labelledby="faq-h">
  <div class="wrap">
    <div class="head" style="margin-bottom:40px"><h2 id="faq-h">常见问题</h2></div>
    <div class="faq">
{faq}
    </div>
  </div>
</section>"""
    return head(f"联系与常见问题 · {BRAND} · 诸暨山下湖",
                f"联系玺爱珠宝：致电或微信联系陈先生 {PHONE}，或到诸暨山下湖展厅参观。附常见问题解答。",
                "/contact", "/images/showroom.jpg", ld) + header("contact") + body + footer()


def not_found():
    body = """<div class="wrap" style="padding:120px 16px 140px;text-align:center">
  <h1 style="font-size:clamp(28px,3vw,40px)">这个页面已移动</h1>
  <p class="sub" style="margin:16px auto 34px">浏览全部珠宝，或用货号向我们咨询任意款式。</p>
  <div class="btns" style="justify-content:center"><a class="btn fill" href="/products">全部珠宝</a><a class="btn" href="/contact">联系我们</a></div>
</div>"""
    return head(f"页面未找到 · {BRAND}", "找不到这个页面。", "/404", "/images/showroom.jpg") + header() + body + footer()


# -------------------------------------------------------------- build -----
def main():
    missing = [k for k in ("hero", "mixed", "ring") if k not in CAMPAIGN]
    small = [k for k, v in CAMPAIGN.items() if size(v["src"])[0] < 1000]
    if missing:
        print("note: campaign images not found, sections skipped:", ", ".join(missing))
    if small:
        print("WARNING: campaign images below 1000px wide (placeholders?):", ", ".join(small))
        if "--allow-small" not in sys.argv:
            sys.exit("refusing to build with low-resolution campaign images; pass --allow-small for a local preview")
    write("index.html", home())
    write("products/index.html", listing())
    for c in CATEGORIES:
        write(f"products/{c['slug']}.html", listing(c))
    for p in products:
        write(f"products/{p['sku']}.html", product(p))
    write("pearl-guide.html", guide())
    write("our-story.html", story())
    write("wholesale.html", wholesale())
    write("contact.html", contact())
    write("404.html", not_found())
    urls = ["/", "/products"] + [f"/products/{c['slug']}" for c in CATEGORIES] + [f"/products/{p['sku']}" for p in products] + \
           ["/pearl-guide", "/our-story", "/wholesale", "/contact"]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sm += "".join(f"  <url><loc>{SITE}{u}</loc></url>\n" for u in urls) + "</urlset>\n"
    (ROOT / "sitemap.xml").write_text(sm, encoding="utf-8")
    print(f"sitemap.xml: {len(urls)} urls; {len(products)} products")


if __name__ == "__main__":
    main()
