import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bs4 import BeautifulSoup
from scrapers.utils import safe_get
from database import save_raw_scrape

# Better sources (search pages are unreliable)
START_URLS = [
    "https://www.dawn.com/latest-news",
    "https://www.dawn.com/pakistan",
    "https://www.dawn.com/sport"
]

KEYWORDS = [
    "road", "highway", "pass", "karakoram", "kkh", "gilgit",
    "hunza", "skardu", "babusar", "landslide", "closure",
    "blocked", "naran", "flood", "weather"
]


def scrape_dawn():
    print("[Dawn] Starting...")

    article_urls = set()

    # STEP 1: collect links
    for url in START_URLS:
        response = safe_get(url)

        if not response:
            continue

        soup = BeautifulSoup(response.text, "html.parser")

        for a in soup.find_all("a", href=True):
            href = a["href"]

            if not href:
                continue

            # keep only article links
            if "/news/" not in href and "/202" not in href:
                continue

            full_url = href if href.startswith("http") else "https://www.dawn.com" + href

            article_urls.add(full_url)

    print(f"[Dawn] Found {len(article_urls)} links")

    # STEP 2: scrape articles
    count = 0

    for url in list(article_urls)[:10]:
        r = safe_get(url)

        if not r:
            continue

        soup = BeautifulSoup(r.text, "html.parser")

        content = (
            soup.find("div", class_="story__content")
            or soup.find("article")
            or soup.find("main")
        )

        if not content:
            continue

        text = content.get_text(separator=" ", strip=True).lower()

        # keyword filtering AFTER full extraction (much better)
        if not any(kw in text for kw in KEYWORDS):
            continue

        if len(text) < 100:
            continue

        save_raw_scrape("dawn", url, text[:3000])
        count += 1

    print(f"[Dawn] Saved {count} relevant articles")
    print("[Dawn] Done")


if __name__ == "__main__":
    scrape_dawn()