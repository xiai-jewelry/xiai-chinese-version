#!/usr/bin/env python3
"""按页面实际用字，裁剪思源宋体（Noto Serif CJK SC），生成 fonts/xiai-serif-sc.woff2。

先运行 build_site.py，再在仓库根目录运行：
    python3 scripts/make_font.py [字体文件]

只收录衬线样式的文字（标题、引言、产品卖点、常见问题的问题等，即 site.css 里
用 var(--serif) 的地方），外加全部英文字母、数字和常用标点。改了页面文案后要
重新运行一次，否则新出现的字会用访客电脑上的宋体显示。

字体文件：默认找系统里的 Noto Serif CJK Light；没有的话，从
https://github.com/notofonts/noto-cjk/releases 下载 NotoSerifSC-Light.otf，
把路径作为参数传进来。需要 fontTools 和 brotli：pip install fonttools brotli

许可：Noto Serif CJK 使用 SIL Open Font License 1.1（见 fonts/OFL-NotoSerifCJK.txt）。
按 OFL 的要求，裁剪后的字体改名为 “XIAI Serif SC”，保留原版权声明。
"""
import sys
from html.parser import HTMLParser
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "fonts/xiai-serif-sc.woff2"
CANDIDATES = [
    "/usr/share/fonts/opentype/noto/NotoSerifCJK-Light.ttc",
    "/usr/share/fonts/noto-cjk/NotoSerifCJK-Light.ttc",
    str(Path.home() / "Library/Fonts/NotoSerifSC-Light.otf"),
]
FAMILY = "XIAI Serif SC"
PS_NAME = "XIAISerifSC-Regular"

# 永远收录：英文字母、数字和常用标点（标题里的货号、年份、英文名都用这套字体）。
ALWAYS = "".join(chr(c) for c in range(0x20, 0x7F)) + "“”‘’—–…·、。，：；！？（）《》「」『』【】％＋－～®©　"

HEADINGS = {"h1", "h2", "h3", "h4"}
SERIF_CLASSES = {"sub", "lede", "tagline"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
SKIP = {"script", "style", "title", "template"}


def serif(stack):
    """这段文字在 site.css 里是不是用衬线字体（与 var(--serif) 的选择器对应）。"""
    for i, (tag, cls) in enumerate(stack):
        above = stack[:i]
        acls = set().union(*(c for _, c in above)) if above else set()
        atags = {t for t, _ in above}
        if tag in HEADINGS and not ({"drawer", "foot"} & acls):  # 抽屉菜单和页脚的小标题是黑体
            return True
        if cls & SERIF_CLASSES:
            return True
        if (tag == "summary" and "faq" in acls) or (tag == "p" and "head" in acls) or \
           (tag == "span" and "tile" in acls) or (tag == "b" and {"pearls", "timeline"} & acls) or \
           (tag == "figcaption" and {"mega", "certs"} & acls) or (tag == "li" and "points" in acls) or \
           (tag == "a" and "drawer" in acls and "li" in atags):
            return True
    return False


class Collect(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.skip, self.chars = [], 0, set()

    def handle_starttag(self, tag, attrs):
        if tag in SKIP:
            self.skip += 1
        if tag in VOID:
            return
        self.stack.append((tag, set((dict(attrs).get("class") or "").split())))

    def handle_endtag(self, tag):
        if tag in SKIP:
            self.skip = max(0, self.skip - 1)
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        if not self.skip and data.strip() and serif(self.stack):
            self.chars.update(data)


def sc_font(path):
    """打开字体；.ttc 合集里取简体中文（SC）那一款。"""
    if not path.endswith(".ttc"):
        return TTFont(path)
    for i in range(20):
        f = TTFont(path, fontNumber=i)
        if " SC" in f["name"].getDebugName(1):
            return f
    sys.exit("no SC font in " + path)


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else next((c for c in CANDIDATES if Path(c).exists()), None)
    if not src:
        sys.exit(__doc__)
    pages = [p for p in ROOT.rglob("*.html") if "node_modules" not in p.parts]
    c = Collect()
    for p in pages:
        c.feed(p.read_text(encoding="utf-8"))
        c.close()
        c.reset()
        c.stack, c.skip = [], 0
    text = "".join(sorted(c.chars | set(ALWAYS)))
    cjk = [ch for ch in text if ord(ch) > 0x2E7F]

    font = sc_font(src)
    copyright_ = font["name"].getDebugName(0)
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.hinting = False
    opts.desubroutinize = True
    opts.layout_features = ["kern", "liga", "locl"]
    opts.drop_tables += ["vhea", "vmtx", "VORG", "DSIG"]
    opts.name_IDs = [0, 1, 2, 3, 4, 5, 6, 13, 14]
    sub = subset.Subsetter(opts)
    sub.populate(text=text)
    sub.subset(font)

    name = font["name"]  # OFL：修改后的字体不能沿用原名
    for rec in list(name.names):
        if rec.nameID in (1, 3, 4, 16):
            rec.string = FAMILY
        elif rec.nameID == 6:
            rec.string = PS_NAME
        elif rec.nameID in (2, 17):
            rec.string = "Regular"
    if "CFF " in font:
        cff = font["CFF "].cff
        cff.fontNames = [PS_NAME]
        top = cff.topDictIndex[0]
        for key in ("FullName", "FamilyName"):
            if hasattr(top, key):
                setattr(top, key, FAMILY)
    font.flavor = "woff2"
    OUT.parent.mkdir(exist_ok=True)
    font.save(OUT)
    print(f"{OUT.relative_to(ROOT)}: {len(text)} glyphs ({len(cjk)} Chinese), {OUT.stat().st_size // 1024} KB, from {Path(src).name}")
    print("source copyright:", copyright_)


if __name__ == "__main__":
    main()
