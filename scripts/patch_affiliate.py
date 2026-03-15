#!/usr/bin/env python3
"""
BJJ Wiki - アフィリエイトリンク一括展開
Usage: python3 patch_affiliate.py --ref YOUR_REF_CODE
Run from ~/Claude/bjj-wiki/

BJJ Fanatics アフィリコードの取得方法:
  1. Fanaticsから承認メールを受け取る（Refersion）
  2. ダッシュボードで自分のref codeを確認（例: YOURCODE）
  3. python3 scripts/patch_affiliate.py --ref YOURCODE
"""
import os, re, argparse, glob

BASE = os.path.expanduser("~/Claude/bjj-wiki")
ALREADY_MARKER = "bjjfanatics.com"

# 技slug → (教則タイトル, Fanaticsパス, 著者/シリーズ)
TECHNIQUES = {
    "armbar": (
        "Arm Attacks by Bernardo Faria",
        "/products/arm-attacks",
        "Bernardo Faria"
    ),
    "triangle-choke": (
        "Triangle Machine by Renato Canuto",
        "/products/triangle-machine",
        "Renato Canuto"
    ),
    "rear-naked-choke": (
        "Back Attacks Enter the System by John Danaher",
        "/products/back-attacks-enter-the-system-by-john-danaher",
        "John Danaher"
    ),
    "heel-hook": (
        "Leg Locks Enter the System by John Danaher",
        "/products/leg-locks-enter-the-system-by-john-danaher",
        "John Danaher"
    ),
    "inside-heel-hook": (
        "Leg Locks Enter the System by John Danaher",
        "/products/leg-locks-enter-the-system-by-john-danaher",
        "John Danaher"
    ),
    "outside-heel-hook": (
        "Leg Locks Enter the System by John Danaher",
        "/products/leg-locks-enter-the-system-by-john-danaher",
        "John Danaher"
    ),
    "kimura": (
        "Kimura Trap System by Neil Melanson",
        "/products/kimura-trap-system-by-neil-melanson",
        "Neil Melanson"
    ),
    "guard-pass": (
        "Guard Passing by Bernardo Faria",
        "/products/guard-passing-bernardo-faria",
        "Bernardo Faria"
    ),
    "knee-slice-pass": (
        "Systematically Attacking with the Knee Slice by Lachlan Giles",
        "/products/systematically-attacking-with-the-knee-slice-by-lachlan-giles",
        "Lachlan Giles"
    ),
    "torreando-pass": (
        "Guard Passing by Bernardo Faria",
        "/products/guard-passing-bernardo-faria",
        "Bernardo Faria"
    ),
    "leg-drag-pass": (
        "Guard Passing by Bernardo Faria",
        "/products/guard-passing-bernardo-faria",
        "Bernardo Faria"
    ),
    "berimbolo": (
        "Berimbolo System by Caio Terra",
        "/products/berimbolo-system-by-caio-terra",
        "Caio Terra"
    ),
    "de-la-riva-guard": (
        "De La Riva Guard by Rafael Freitas",
        "/products/de-la-riva-guard-by-rafael-freitas",
        "Rafael Freitas"
    ),
    "spider-guard": (
        "Spider Guard by Leo Nogueira",
        "/products/spider-guard-leo-nogueira",
        "Leo Nogueira"
    ),
    "worm-guard": (
        "Worm Guard by Keenan Cornelius",
        "/products/worm-guard-by-keenan-cornelius",
        "Keenan Cornelius"
    ),
    "x-guard": (
        "X Guard by Marcelo Garcia",
        "/products/x-guard-by-marcelo-garcia",
        "Marcelo Garcia"
    ),
    "butterfly-guard": (
        "Butterfly Guard by Marcelo Garcia",
        "/products/butterfly-guard-by-marcelo-garcia",
        "Marcelo Garcia"
    ),
    "closed-guard": (
        "Closed Guard by Bernardo Faria",
        "/products/closed-guard-bernardo-faria",
        "Bernardo Faria"
    ),
    "half-guard": (
        "Half Guard by Lucas Leite",
        "/products/half-guard-by-lucas-leite",
        "Lucas Leite"
    ),
    "rubber-guard": (
        "Rubber Guard by Eddie Bravo",
        "/products/rubber-guard-by-eddie-bravo",
        "Eddie Bravo"
    ),
    "open-guard": (
        "Open Guard Passing by Bernardo Faria",
        "/products/guard-passing-bernardo-faria",
        "Bernardo Faria"
    ),
    "mount": (
        "Attacks from Mount by Bernardo Faria",
        "/products/attacks-from-mount",
        "Bernardo Faria"
    ),
    "back-mount": (
        "Back Attacks Enter the System by John Danaher",
        "/products/back-attacks-enter-the-system-by-john-danaher",
        "John Danaher"
    ),
    "side-control": (
        "Side Control by Dean Lister",
        "/products/side-control-submissions",
        "Dean Lister"
    ),
    "north-south": (
        "North South Choke by Marcelo Garcia",
        "/products/north-south-choke-marcelo-garcia",
        "Marcelo Garcia"
    ),
    "knee-on-belly": (
        "Knee on Belly by Bernardo Faria",
        "/products/knee-on-belly",
        "Bernardo Faria"
    ),
    "omoplata": (
        "Omoplata by Robson Moura",
        "/products/omoplata-by-robson-moura",
        "Robson Moura"
    ),
    "americana": (
        "Arm Attacks by Bernardo Faria",
        "/products/arm-attacks",
        "Bernardo Faria"
    ),
    "guillotine-choke": (
        "Guillotine Attacks by Marcelo Garcia",
        "/products/guillotine-attacks-marcelo-garcia",
        "Marcelo Garcia"
    ),
    "darce-choke": (
        "Darce and Anaconda Chokes by Jeff Glover",
        "/products/darce-and-anaconda-chokes-by-jeff-glover",
        "Jeff Glover"
    ),
    "anaconda-choke": (
        "Darce and Anaconda Chokes by Jeff Glover",
        "/products/darce-and-anaconda-chokes-by-jeff-glover",
        "Jeff Glover"
    ),
    "loop-choke": (
        "Gi Chokes by Travis Stevens",
        "/products/gi-chokes-by-travis-stevens",
        "Travis Stevens"
    ),
    "ezekiel-choke": (
        "Gi Chokes by Travis Stevens",
        "/products/gi-chokes-by-travis-stevens",
        "Travis Stevens"
    ),
    "bow-and-arrow-choke": (
        "Back Attacks Enter the System by John Danaher",
        "/products/back-attacks-enter-the-system-by-john-danaher",
        "John Danaher"
    ),
    "toe-hold": (
        "Leg Locks Enter the System by John Danaher",
        "/products/leg-locks-enter-the-system-by-john-danaher",
        "John Danaher"
    ),
    "knee-bar": (
        "Leg Locks Enter the System by John Danaher",
        "/products/leg-locks-enter-the-system-by-john-danaher",
        "John Danaher"
    ),
    "calf-slicer": (
        "Leg Locks Enter the System by John Danaher",
        "/products/leg-locks-enter-the-system-by-john-danaher",
        "John Danaher"
    ),
    "ankle-pick": (
        "Takedowns for BJJ by Travis Stevens",
        "/products/takedowns-for-bjj-by-travis-stevens",
        "Travis Stevens"
    ),
    "double-leg-takedown": (
        "Takedowns for BJJ by Travis Stevens",
        "/products/takedowns-for-bjj-by-travis-stevens",
        "Travis Stevens"
    ),
    "single-leg-takedown": (
        "Takedowns for BJJ by Travis Stevens",
        "/products/takedowns-for-bjj-by-travis-stevens",
        "Travis Stevens"
    ),
    "osoto-gari": (
        "Judo Throws for BJJ by Travis Stevens",
        "/products/judo-throws-for-bjj-by-travis-stevens",
        "Travis Stevens"
    ),
    "sprawl": (
        "Wrestling for BJJ by Bernardo Faria",
        "/products/wrestling-for-bjj",
        "Bernardo Faria"
    ),
    "backtake": (
        "Back Attacks Enter the System by John Danaher",
        "/products/back-attacks-enter-the-system-by-john-danaher",
        "John Danaher"
    ),
    "hip-bump-sweep": (
        "Sweeps from Closed Guard by Bernardo Faria",
        "/products/closed-guard-bernardo-faria",
        "Bernardo Faria"
    ),
    "scissor-sweep": (
        "Sweeps from Closed Guard by Bernardo Faria",
        "/products/closed-guard-bernardo-faria",
        "Bernardo Faria"
    ),
    "pendulum-sweep": (
        "Closed Guard by Bernardo Faria",
        "/products/closed-guard-bernardo-faria",
        "Bernardo Faria"
    ),
    "flower-sweep": (
        "Closed Guard by Bernardo Faria",
        "/products/closed-guard-bernardo-faria",
        "Bernardo Faria"
    ),
    "headquarters-pass": (
        "Guard Passing by Bernardo Faria",
        "/products/guard-passing-bernardo-faria",
        "Bernardo Faria"
    ),
    "turtle-position": (
        "Back Attacks Enter the System by John Danaher",
        "/products/back-attacks-enter-the-system-by-john-danaher",
        "John Danaher"
    ),
    "wrist-lock": (
        "Wristlocks From Everywhere by Budo Jake",
        "/products/wristlocks-from-everywhere",
        "Budo Jake"
    ),
}

DEFAULT_PRODUCT = ("/collections/all", "Browse All BJJ Instructionals", "BJJ Fanatics")


def build_block(slug, ref_code):
    title, path, author = TECHNIQUES.get(slug, DEFAULT_PRODUCT)
    if slug not in TECHNIQUES:
        title, author = DEFAULT_PRODUCT[1], DEFAULT_PRODUCT[2]
        path = DEFAULT_PRODUCT[0]
        search_query = slug.replace("-", "+")
        url = f"https://bjjfanatics.com/collections/all?q={search_query}&ref={ref_code}"
    else:
        url = f"https://bjjfanatics.com{path}?ref={ref_code}"

    return f"""
<!-- BJJ Fanatics Affiliate -->
<section class="affiliate-section" style="max-width:680px;margin:32px auto;padding:20px 24px;background:linear-gradient(135deg,#1e293b 0%,#0f172a 100%);border-radius:12px;color:#fff;display:flex;align-items:center;gap:20px;flex-wrap:wrap;">
  <div style="flex:1;min-width:200px;">
    <p style="margin:0 0 4px;font-size:0.75rem;color:#94a3b8;text-transform:uppercase;letter-spacing:0.05em;">📚 おすすめ教則 / Recommended Instructional</p>
    <p style="margin:0 0 8px;font-size:1rem;font-weight:700;line-height:1.4;">{title}</p>
    <p style="margin:0;font-size:0.8rem;color:#94a3b8;">by {author} — BJJ Fanatics</p>
  </div>
  <a href="{url}" target="_blank" rel="noopener nofollow"
     style="display:inline-block;padding:10px 20px;background:#ef4444;color:#fff;border-radius:8px;font-size:0.85rem;font-weight:700;text-decoration:none;white-space:nowrap;transition:background 0.2s;"
     onmouseover="this.style.background='#dc2626'" onmouseout="this.style.background='#ef4444'">
    今すぐ学ぶ →
  </a>
</section>
<!-- /BJJ Fanatics Affiliate -->
"""


def patch_file(path, slug, ref_code):
    with open(path, encoding="utf-8") as f:
        html = f.read()

    if ALREADY_MARKER in html:
        return "skip"

    block = build_block(slug, ref_code)

    # yt-wrapの後（動画の下）に挿入、なければ</main>か</body>の前
    if 'class="yt-wrap"' in html:
        html = re.sub(
            r'(</div>\s*<!-- /yt-wrap -->)',
            r'\1\n' + block,
            html, count=1
        )
    elif "</main>" in html:
        html = html.replace("</main>", block + "\n</main>", 1)
    else:
        html = html.replace("</body>", block + "\n</body>", 1)

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return "ok"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ref", required=True, help="BJJ Fanaticsのrefコード（例: YOURCODE）")
    parser.add_argument("--dry-run", action="store_true", help="変更せずプレビューのみ")
    args = parser.parse_args()

    ok = skip = 0
    for lang in ["en", "ja", "pt"]:
        html_files = glob.glob(os.path.join(BASE, lang, "*.html"))
        for path in sorted(html_files):
            fname = os.path.basename(path)
            if fname == "index.html":
                continue
            slug = fname.replace(".html", "")
            rel = os.path.relpath(path, BASE)

            if args.dry_run:
                has_entry = slug in TECHNIQUES
                print(f"{'[MAP]' if has_entry else '[GEN]'} {rel}")
                ok += 1
                continue

            result = patch_file(path, slug, args.ref)
            if result == "ok":
                has_entry = slug in TECHNIQUES
                print(f"[OK] {rel} {'(specific)' if has_entry else '(generic)'}")
                ok += 1
            else:
                skip += 1

    if args.dry_run:
        print(f"\n[ドライラン] {ok}件が対象（実際は変更なし）")
    else:
        print(f"\n[完了] {ok}件を更新（スキップ {skip}件）")


if __name__ == "__main__":
    main()
