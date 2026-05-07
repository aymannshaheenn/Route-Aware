import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bs4 import BeautifulSoup
from scrapers.utils import safe_get
from database import save_raw_scrape

PMD_URLS = [
    "https://www.pmd.gov.pk/en/weather-warnings.php",
    "https://www.pmd.gov.pk/en/press-releases.php",
]


def scrape_pmd():
    print("[PMD] Starting...")

    for url in PMD_URLS:
        response = safe_get(url)
        if not response:
            continue
        soup = BeautifulSoup(response.text, "html.parser")
        content = (soup.find("div", class_="content")
                   or soup.find("main")
                   or soup.find("body"))
        if content:
            text = content.get_text(separator=" ", strip=True)
            if len(text) > 50:
                save_raw_scrape("pmd", url, text[:3000])
                print(f"[PMD] Saved: {url}")

    print("[PMD] Done")


if __name__ == "__main__":
    scrape_pmd()