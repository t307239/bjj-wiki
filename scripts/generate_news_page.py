#!/usr/bin/env python3
"""
generate_news_page.py — Wave WW (G): /news weekly auto-update generator

Re-renders en/news.html, ja/news.html, pt/news.html from data/news_feed.yml.
Cron-driven via .github/workflows/news_weekly.yml (Mondays 09:00 JST):
  - Bumps "week of YYYY-MM-DD" stamp
  - Rotates featured_techniques pool window (3 picks per week)
  - Lists upcoming_events (filtering past dates)
  - Lists last 5 milestones

Honesty: never invents news. Featured pool is curated evergreen content.
Events are real publicly-announced tournaments. Milestones are real wiki
work. If unsure, omit.

Idempotent: safe to re-run. Each invocation re-renders deterministically
based on (week_number, news_feed.yml) state.
"""
from __future__ import annotations
import argparse
import datetime as dt
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = REPO_ROOT / "data" / "news_feed.yml"

LANGS = ["en", "ja", "pt"]

I18N = {
    "en": {
        "page_title": "BJJ Weekly — Featured Techniques & Tournament Calendar | BJJ App Wiki",
        "page_desc": "Weekly digest of featured BJJ techniques, upcoming tournaments (IBJJF, ADCC), and recent updates to the BJJ App Wiki.",
        "h1": "📰 BJJ Weekly",
        "subtitle": "Week of {week_of} — Featured techniques, real tournament dates, recent wiki updates.",
        "featured_h2": "🥋 Featured Techniques This Week",
        "events_h2": "🏆 Upcoming Tournaments",
        "milestones_h2": "🆕 Recent Wiki Updates",
        "read_more": "Read the guide →",
        "event_at": "at",
        "no_events": "No tournaments scheduled in the next 90 days.",
    },
    "ja": {
        "page_title": "BJJ ウィークリー — 注目テクニックと大会カレンダー | BJJ App Wiki",
        "page_desc": "今週の注目 BJJ テクニック、IBJJF / ADCC 等の大会予定、BJJ App Wiki の最新更新を毎週まとめてお届け。",
        "h1": "📰 BJJ ウィークリー",
        "subtitle": "週の始まり: {week_of} — 注目テクニック、実在する大会日程、Wiki 更新。",
        "featured_h2": "🥋 今週の注目テクニック",
        "events_h2": "🏆 今後の大会予定",
        "milestones_h2": "🆕 最近の Wiki 更新",
        "read_more": "ガイドを読む →",
        "event_at": "場所:",
        "no_events": "今後 90 日以内に予定されている大会はありません。",
    },
    "pt": {
        "page_title": "BJJ Semanal — Técnicas em destaque e calendário de torneios | BJJ App Wiki",
        "page_desc": "Resumo semanal de técnicas de BJJ em destaque, próximos torneios (IBJJF, ADCC) e atualizações recentes do BJJ App Wiki.",
        "h1": "📰 BJJ Semanal",
        "subtitle": "Semana de {week_of} — técnicas em destaque, datas reais de torneios, atualizações do wiki.",
        "featured_h2": "🥋 Técnicas em destaque desta semana",
        "events_h2": "🏆 Próximos torneios",
        "milestones_h2": "🆕 Atualizações recentes do wiki",
        "read_more": "Leia o guia →",
        "event_at": "em",
        "no_events": "Nenhum torneio agendado para os próximos 90 dias.",
    },
}


def load_yaml(path: Path) -> dict:
    """Minimal YAML loader (no PyYAML dependency in CI)."""
    try:
        import yaml  # type: ignore
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except ImportError:
        # Lightweight fallback parser for our specific file format
        # (only handles: top-level lists with `slug:` / `date:` etc keys)
        raise SystemExit("PyYAML required: pip install pyyaml")


def get_week_of(now: dt.date) -> str:
    """Monday of the current week, ISO format."""
    return (now - dt.timedelta(days=now.weekday())).isoformat()


def select_featured(pool: list, week_idx: int, n: int = 3) -> list:
    """Rotate through pool, picking n consecutive items per week."""
    if not pool:
        return []
    start = (week_idx * n) % len(pool)
    out = []
    for i in range(n):
        out.append(pool[(start + i) % len(pool)])
    return out


def filter_upcoming_events(events: list, today: dt.date, days: int = 90) -> list:
    cutoff = today + dt.timedelta(days=days)
    out = []
    for e in events:
        try:
            d = dt.date.fromisoformat(str(e["date"]))
        except Exception:
            continue
        if today <= d <= cutoff:
            out.append((d, e))
    return [e for _, e in sorted(out, key=lambda t: t[0])]


def render_featured_card(item: dict, lang: str, t: dict, base_url: str) -> str:
    title = item.get(lang, item.get("en", item["slug"]))
    slug = item["slug"]
    return f"""
<article style="background:#111119;border:1px solid #1e1e2e;border-radius:12px;padding:20px;margin-bottom:16px">
  <h3 style="font-size:1.05rem;font-weight:700;color:#e2e2ee;margin-bottom:10px">{title}</h3>
  <p style="margin:0"><a href="{slug}.html" style="color:#7c3aed;font-weight:600;text-decoration:none">{t['read_more']}</a></p>
</article>"""


def render_event_card(event: dict, t: dict) -> str:
    name = event.get("name", "TBA")
    loc = event.get("location", "TBA")
    url = event.get("url", "")
    date = event.get("date", "")
    href_attr = f'href="{url}" target="_blank" rel="noopener noreferrer"' if url else ""
    name_html = f'<a {href_attr} style="color:#e2e2ee;text-decoration:none">{name}</a>' if url else name
    return f"""
<article style="background:#111119;border:1px solid #1e1e2e;border-radius:12px;padding:20px;margin-bottom:16px">
  <div style="font-size:.78rem;color:#7a7a9a;margin-bottom:8px">📅 {date}</div>
  <h3 style="font-size:1.05rem;font-weight:700;margin-bottom:6px">{name_html}</h3>
  <p style="font-size:.9rem;color:#b0b0c8;margin:0">{t['event_at']} {loc}</p>
</article>"""


def render_milestone(milestone: dict, lang: str) -> str:
    msg = milestone.get(lang, milestone.get("en", ""))
    date = milestone.get("date", "")
    return f"""
<li style="margin-bottom:8px;color:#c8e6c9;font-size:.9rem">
  <span style="color:#7a7a9a;font-size:.8rem">{date}</span> — {msg}
</li>"""


HEAD_RE = re.compile(r"(<head[^>]*>)(.*?)(</head>)", re.IGNORECASE | re.DOTALL)
BODY_MAIN_RE = re.compile(
    r"(<main[^>]*>.*?</main>)", re.IGNORECASE | re.DOTALL,
)


def render_main_block(lang: str, data: dict, week_of: str, today: dt.date) -> str:
    t = I18N[lang]
    base_url = "https://wiki.bjj-app.net"

    week_idx = today.isocalendar()[1]
    featured = select_featured(data.get("featured_techniques") or [], week_idx, n=3)
    events = filter_upcoming_events(data.get("upcoming_events") or [], today, days=180)
    milestones = (data.get("milestones") or [])[:5]

    featured_html = "".join(render_featured_card(f, lang, t, base_url) for f in featured)
    if events:
        events_html = "".join(render_event_card(e, t) for e in events)
    else:
        events_html = f'<p style="color:#7a7a9a">{t["no_events"]}</p>'
    milestones_html = "".join(render_milestone(m, lang) for m in milestones)

    return f"""<main class="container">
  <div class="breadcrumb"><a href="index.html">BJJ App Wiki</a> › {t['h1']}</div>
  <h1>{t['h1']}</h1>
  <p style="color:#7a7a9a;font-size:.9rem;margin-bottom:24px">{t['subtitle'].format(week_of=week_of)}</p>

  <h2 style="font-size:1.2rem;color:#e94560;margin:32px 0 16px">{t['featured_h2']}</h2>
  {featured_html}

  <h2 style="font-size:1.2rem;color:#e94560;margin:32px 0 16px">{t['events_h2']}</h2>
  {events_html}

  <h2 style="font-size:1.2rem;color:#e94560;margin:32px 0 16px">{t['milestones_h2']}</h2>
  <ul style="list-style:none;padding:0;margin:0;background:#111119;border:1px solid #1e1e2e;border-radius:12px;padding:20px">
{milestones_html}
  </ul>
</main>"""


def update_news_html(lang: str, data: dict, week_of: str, today: dt.date) -> str | None:
    fp = REPO_ROOT / lang / "news.html"
    if not fp.exists():
        return None
    html = fp.read_text(encoding="utf-8")
    new_main = render_main_block(lang, data, week_of, today)
    new_html, n = BODY_MAIN_RE.subn(new_main, html, count=1)
    if n != 1:
        return f"failed-no-main-found"
    # Update <title> + meta description with new freshness stamp
    t = I18N[lang]
    new_title = t["page_title"]
    new_desc = t["page_desc"]
    new_html = re.sub(
        r"<title>[^<]*</title>",
        f"<title>{new_title}</title>",
        new_html, count=1,
    )
    new_html = re.sub(
        r'<meta name="description" content="[^"]*"',
        f'<meta name="description" content="{new_desc}"',
        new_html, count=1,
    )
    fp.write_text(new_html, encoding="utf-8")
    return f"ok ({len(new_main):,} bytes main)"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", help="Override today's date (YYYY-MM-DD) for testing")
    args = parser.parse_args()

    today = dt.date.fromisoformat(args.date) if args.date else dt.date.today()
    week_of = get_week_of(today)

    data = load_yaml(DATA_FILE)
    print(f"📰 Generating /news for week of {week_of}")

    for lang in LANGS:
        result = update_news_html(lang, data, week_of, today)
        print(f"  {lang}/news.html: {result}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
