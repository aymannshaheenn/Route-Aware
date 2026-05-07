import sys, os, time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from bs4 import BeautifulSoup
from database import save_raw_scrape

FB_URL = "https://mobile.facebook.com/groups/PakistanTourism"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
}
KEYWORDS = ["road", "pass", "blocked", "open", "closed", "landslide",
            "snow", "kkh", "karakoram", "babusar", "naran", "hunza", "gilgit"]


def scrape_facebook():
    print("[Facebook] Starting...")
    try:
        time.sleep(2)
        response = httpx.get(FB_URL, headers=HEADERS, timeout=20)
        soup = BeautifulSoup(response.text, "html.parser")

        posts = (soup.find_all("div", class_="story_body_container")
                 or soup.find_all("div", class_="_5pcr")
                 or soup.find_all("div", {"data-ft": True}))

        saved = 0
        for post in posts[:10]:
            text = post.get_text(separator=" ", strip=True)
            if any(kw in text.lower() for kw in KEYWORDS) and len(text) > 30:
                save_raw_scrape("facebook", FB_URL, text[:2000])
                saved += 1
                time.sleep(1)

        print(f"[Facebook] Saved {saved} posts")

    except Exception as e:
        print(f"[Facebook ERROR] {e} — skipping, other scrapers still work")

    print("[Facebook] Done")


if __name__ == "__main__":
    scrape_facebook()