#!/usr/bin/env python3
"""
gen_og_png.py
=============
SVG OG画像 → PNG変換。Pinterest/X/Threads等のSNSプラットフォーム向け。
SVGをサポートしないプラットフォーム（Pinterest等）用にPNG版を生成。

依存: pip install cairosvg   (GHA: pip install cairosvg)
代替: Pillowベースの直接生成にフォールバック

Usage:
    python3 scripts/gen_og_png.py                   # 全ページ変換
    python3 scripts/gen_og_png.py --lang en          # 英語のみ
    python3 scripts/gen_og_png.py --slug bjj-guard   # 特定ページのみ
    python3 scripts/gen_og_png.py --incremental      # 未変換のみ
"""
import os
import sys
import glob

WIKI_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OG_SVG_DIR = os.path.join(WIKI_ROOT, "og")
OG_PNG_DIR = os.path.join(WIKI_ROOT, "og-png")


def convert_svg_to_png_cairosvg(svg_path: str, png_path: str) -> bool:
    """cairosvgでSVG→PNG変換"""
    try:
        import cairosvg
        cairosvg.svg2png(url=svg_path, write_to=png_path, output_width=1200, output_height=630)
        return True
    except ImportError:
        return False
    except Exception as e:
        print(f"  [WARN] cairosvg failed for {svg_path}: {e}")
        return False


def generate_png_pillow(title: str, lang: str, png_path: str) -> bool:
    """Pillowでテキストベースの簡易PNG OG画像を生成（cairosvg非依存）"""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("[FATAL] Neither cairosvg nor Pillow installed. pip install cairosvg OR Pillow")
        return False

    W, H = 1200, 630
    img = Image.new("RGB", (W, H), color=(11, 17, 32))  # #0B1120
    draw = ImageDraw.Draw(img)

    # グラデーション風の背景（簡易）
    for y in range(H):
        r = int(11 + (20 - 11) * (y / H) * 0.5)
        g = int(17 + (25 - 17) * (y / H) * 0.5)
        b = int(32 + (48 - 32) * (y / H) * 0.5)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # アクセントライン（上下）
    draw.rectangle([0, 0, W, 5], fill=(124, 106, 247))   # #7c6af7
    draw.rectangle([0, H - 5, W, H], fill=(124, 106, 247))

    # フォント設定（システムフォントにフォールバック）
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    title_font = None
    small_font = None
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                title_font = ImageFont.truetype(fp, 48)
                small_font = ImageFont.truetype(fp, 22)
                break
            except Exception:
                continue
    if not title_font:
        title_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # BJJ WIKI ヘッダー
    draw.text((W // 2, 140), "BJJ WIKI", fill=(107, 118, 153), font=small_font, anchor="mm")

    # タイトル（複数行対応）
    words = title.split()
    lines = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        if len(test) > 30 and current:
            lines.append(current)
            current = word
        else:
            current = test
    if current:
        lines.append(current)
    lines = lines[:3]

    y_start = 280 if len(lines) <= 2 else 250
    line_h = 62
    for i, line in enumerate(lines):
        y = y_start + i * line_h
        draw.text((W // 2, y), line, fill=(232, 234, 246), font=title_font, anchor="mm")

    # フッター
    draw.text((W // 2, 500), "wiki.bjj-app.net", fill=(74, 81, 112), font=small_font, anchor="mm")

    # 言語バッジ
    lang_labels = {"en": "English", "ja": "Japanese", "pt": "Portuguese"}
    badge_text = lang_labels.get(lang, lang.upper())
    draw.text((W // 2, 545), badge_text, fill=(167, 139, 250), font=small_font, anchor="mm")

    img.save(png_path, "PNG", optimize=True)
    return True


def extract_title_from_svg(svg_path: str) -> str:
    """SVGファイルからタイトルテキストを抽出"""
    import re
    try:
        with open(svg_path, "r", encoding="utf-8") as f:
            content = f.read()
        # font-size 40以上のテキスト要素からタイトルを取得
        texts = re.findall(r'font-size="(\d+)"[^>]*>([^<]+)</text>', content)
        title_parts = []
        for size_str, text in texts:
            size = int(size_str)
            if size >= 36:
                import html
                title_parts.append(html.unescape(text.strip()))
        return " ".join(title_parts) if title_parts else ""
    except Exception:
        return ""


def main():
    incremental = "--incremental" in sys.argv
    target_lang = None
    target_slug = None

    for i, arg in enumerate(sys.argv):
        if arg == "--lang" and i + 1 < len(sys.argv):
            target_lang = sys.argv[i + 1]
        if arg == "--slug" and i + 1 < len(sys.argv):
            target_slug = sys.argv[i + 1]

    os.makedirs(OG_PNG_DIR, exist_ok=True)

    # SVGファイル一覧
    pattern = os.path.join(OG_SVG_DIR, "*.svg")
    svg_files = sorted(glob.glob(pattern))

    if target_lang:
        svg_files = [f for f in svg_files if os.path.basename(f).startswith(f"{target_lang}-")]
    if target_slug:
        svg_files = [f for f in svg_files if target_slug in os.path.basename(f)]

    total = len(svg_files)
    converted = 0
    skipped = 0

    # cairosvgの利用可否チェック
    use_cairosvg = False
    try:
        import cairosvg
        use_cairosvg = True
        print(f"[INFO] Using cairosvg for SVG→PNG conversion")
    except ImportError:
        print(f"[INFO] cairosvg not found, using Pillow fallback")

    for svg_path in svg_files:
        basename = os.path.basename(svg_path)
        png_name = basename.replace(".svg", ".png")
        png_path = os.path.join(OG_PNG_DIR, png_name)

        if incremental and os.path.exists(png_path):
            skipped += 1
            continue

        # 言語抽出
        lang = basename.split("-")[0] if "-" in basename else "en"

        if use_cairosvg:
            ok = convert_svg_to_png_cairosvg(svg_path, png_path)
        else:
            title = extract_title_from_svg(svg_path)
            if not title:
                title = basename.replace(".svg", "").replace(f"{lang}-", "").replace("-", " ").title()
            ok = generate_png_pillow(title, lang, png_path)

        if ok:
            converted += 1
        if converted <= 3:
            print(f"  {basename} → {png_name}")
        elif converted == 4:
            print(f"  ... ({total - skipped} remaining)")

    print(f"\n=== PNG生成完了: {converted}件変換, {skipped}件スキップ (全{total}件) ===")
    print(f"出力先: {OG_PNG_DIR}/")


if __name__ == "__main__":
    main()
