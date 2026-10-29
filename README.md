# 玺爱珠宝中文官网 · XIAI Jewelry (Chinese)

玺爱珠宝品牌官网的中文版（静态多页面网站），与英文版 https://xiai-jewelry.github.io 页面结构一一对应，只把全部内容换成了中文。

- 正式地址：https://xiai-jewelry.cn （GitHub Pages 托管，服务器在境外，国内可直接访问，不需要 ICP 备案）
- 备用地址：https://xiai-jewelry.github.io/xiai-chinese-version/ 会自动跳到正式地址
- 英文版源码：`Sophia-ZHANG101/xiai-website`

## 页面
- `/` 首页 · `/products` 全部珠宝 · `/products/<品类>` 品类页（necklaces 项链 / earrings 耳饰 / rings 戒指 / bracelets 手链手镯 / pendants 吊坠 / brooches 胸针）
- `/products/<货号>` 产品详情页（32 款）
- `/pearl-guide` 珍珠指南 · `/our-story` 品牌故事 · `/wholesale` 批发与定制 · `/contact` 联系与常见问题

## 怎么改
- 产品资料：`data/products.json`，中文名称、一句话卖点、简介、卖点、适合人群都来自企业《SKU 信息收集表》的「官网文案」页；参数、常见问题与英文版一致。不要加表里没有的款式。
- 页面结构和文案：`scripts/build_site.py`；样式：`assets/site.css`（末尾是中文排版部分）；交互：`assets/site.js`。
- 改完依次运行：
  1. `python3 scripts/build_site.py`：重新生成所有 HTML 和 `sitemap.xml`（不要手改生成出来的 HTML）。
  2. `python3 scripts/make_font.py`：按页面用字重新裁剪标题用的宋体 `fonts/xiai-serif-sc.woff2`（思源宋体 Noto Serif CJK 的子集，约 180KB）。文案里出现新字时必须运行，否则新字会用访客电脑上的宋体显示。需要 `pip install fonttools brotli`，字体文件的获取方法写在脚本开头。
- 字体：标题用自托管的宋体子集，正文用系统自带的苹方 / 微软雅黑，数字和英文用 Jost。全部字体都放在本站，不引用 Google Fonts（国内打不开）。
- 首页轮播、人物试戴、品牌影片、页面滚动动效的说明见英文版 README，两边做法相同。
- 配色（奶咖·米色）和英文版相同，在 `assets/site.css` 开头的 `:root` 里。

## 部署
- 推送到本仓库 `main` 分支，GitHub Pages 会自动发布（Settings → Pages：Deploy from a branch，main，/ (root)）。
- 自定义域名：仓库根目录的 `CNAME` 文件写着 `xiai-jewelry.cn`。域名在腾讯云 DNSPod 解析：
  - `@` 四条 A 记录：185.199.108.153、185.199.109.153、185.199.110.153、185.199.111.153
  - `www` 一条 CNAME 记录：xiai-jewelry.github.io
- 解析生效后，在 Settings → Pages 勾选 Enforce HTTPS。
