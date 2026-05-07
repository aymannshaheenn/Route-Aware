import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bs4 import BeautifulSoup
from scrapers.utils import safe_get
from database import save_raw_scrape

NDMA_URLS = [
    "https://ndma.gov.pk/news/",
    "https://ndma.gov.pk/alerts/",
]


def scrape_ndma():
    print("[NDMA] Starting...")

    for base_url in NDMA_URLS:
        response = safe_get(base_url)
        if not response:
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        links = []

        for a in soup.find_all("a", href=True):
            href = a["href"]
            if not href.startswith("http"):
                href = "https://ndma.gov.pk" + href
            if "ndma.gov.pk" in href and href != base_url and href not in links:
                links.append(href)

        for url in links[:6]:
            r = safe_get(url)
            if not r:
                continue
            s = BeautifulSoup(r.text, "html.parser")
            content = (s.find("div", class_="entry-content")
                       or s.find("main")
                       or s.find("article"))
            if content:
                text = content.get_text(separator=" ", strip=True)
                if len(text) > 50:
                    save_raw_scrape("ndma", url, text[:3000])
                    print(f"[NDMA] Saved: {url}")

    print("[NDMA] Done")


if __name__ == "__main__":
    scrape_ndma()