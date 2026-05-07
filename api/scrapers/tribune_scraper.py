import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bs4 import BeautifulSoup
from scrapers.utils import safe_get
from database import save_raw_scrape

SEARCH_URLS = [
    "https://tribune.com.pk/?s=karakoram+highway",
    "https://tribune.com.pk/?s=road+closure+gilgit",
]

KEYWORDS = ["road", "highway", "pass", "karakoram", "gilgit", "hunza",
            "skardu", "babusar", "landslide", "closure", "blocked"]


def scrape_tribune():
    print("[Tribune] Starting...")
    article_urls = []

    for search_url in SEARCH_URLS:
        response = safe_get(search_url)
        if not response:
            continue
        soup = BeautifulSoup(response.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text().lower()
            if any(kw in text for kw in KEYWORDS):
                if not href.startswith("http"):
                    href = "https://tribune.com.pk" + href
                if href not in article_urls and "tribune.com.pk" in href:
                    article_urls.append(href)

    print(f"[Tribune] Found {len(article_urls)} links")

    for url in article_urls[:6]:
        r = safe_get(url)
        if not r:
            continue
        s = BeautifulSoup(r.text, "html.parser")
        content = (s.find("div", class_="story-body")
                   or s.find("article")
                   or s.find("main"))
        if content:
            text = content.get_text(separator=" ", strip=True)
            if len(text) > 100:
                save_raw_scrape("tribune", url, text[:3000])

    print("[Tribune] Done")


if __name__ == "__main__":
    scrape_tribune()