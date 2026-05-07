import cloudscraper

scraper = cloudscraper.create_scraper()

def safe_get(url):
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        }

        response = scraper.get(url, headers=headers, timeout=15)

        if response.status_code != 200:
            print(f"[HTTP] {response.status_code} -> {url}")
            return None

        return response

    except Exception as e:
        print(f"[HTTP ERROR] {url}: {e}")
        return None