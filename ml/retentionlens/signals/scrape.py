"""Competitive-intelligence scraping demo (week 10) on books.toscrape.com, a sandbox built to be scraped.

Polite by design: checks robots.txt, identifies itself, waits between requests, caches pages and
never logs in or bypasses access controls.
"""
from __future__ import annotations

import html
import re
import time
import urllib.error
import urllib.request
import urllib.robotparser
from pathlib import Path

BASE = "https://books.toscrape.com/"
USER_AGENT = "RetentionLens-coursework/0.3 (MAIB AI 208; github.com/krish2105)"
RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
PRODUCT = re.compile(
    r'<article class="product_pod">.*?star-rating (\w+).*?<h3><a href="[^"]+" title="([^"]+)">.*?class="price_color">([^<]+)<.*?availability">\s*(?:<i[^>]*></i>)?\s*([^<]+?)\s*<',
    re.S,
)


def parse_listing(page: str) -> list[dict]:
    items = []
    for rating, title, price, stock in PRODUCT.findall(page):
        items.append({"title": html.unescape(title), "price_gbp": float(re.sub(r"[^\d.]", "", price)), "rating": RATINGS.get(rating, 0), "in_stock": "In stock" in stock})
    return items


def allowed(url: str) -> bool:
    robots = urllib.robotparser.RobotFileParser(BASE + "robots.txt")
    try:
        robots.read()
    except (urllib.error.URLError, OSError):
        return False
    return robots.can_fetch(USER_AGENT, url) or robots.default_entry is None


def scrape(cache_dir: Path, pages: int = 3, delay: float = 1.0) -> dict:
    cache_dir.mkdir(parents=True, exist_ok=True)
    items, fetched, log = [], 0, []
    for n in range(1, pages + 1):
        url = f"{BASE}catalogue/page-{n}.html"
        cached = cache_dir / f"toscrape_page_{n}.html"
        if not cached.exists():
            if not allowed(url):
                log.append(f"robots.txt disallows {url}; skipped")
                continue
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=20) as response:
                cached.write_text(response.read().decode("utf-8"))
            fetched += 1
            time.sleep(delay)
        items.extend(parse_listing(cached.read_text()))
    by_rating = {}
    for r in range(1, 6):
        prices = [i["price_gbp"] for i in items if i["rating"] == r]
        if prices:
            by_rating[str(r)] = {"items": len(prices), "mean_price": round(sum(prices) / len(prices), 2)}
    return {
        "site": BASE,
        "pages": pages,
        "fetched_now": fetched,
        "items": len(items),
        "price_by_rating": by_rating,
        "sample": items[:10],
        "log": log,
        "practice": ["robots.txt checked before each new fetch", "identifying User-Agent", f"{delay}s delay between requests", "responses cached; nothing behind a login"],
    }
