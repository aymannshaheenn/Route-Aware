import os
import sys
import json
import time
from dotenv import load_dotenv
from google import genai

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import (
    get_unprocessed_scrapes,
    save_event,
    mark_scrape_processed
)

# -------------------------
# LOAD ENV
# -------------------------
load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# -------------------------
# QUOTA FLAG
# -------------------------
GEMINI_QUOTA_EXHAUSTED = False

# -------------------------
# PROMPT
# -------------------------
PROMPT = """You are a road condition analyst for Northern Pakistan.

Extract road events from the text.

Return ONLY a JSON array.

Each item must include:
- route_name
- event_type (landslide, snow, closure, checkpoint, weather_warning, advisory, open)
- description
- location_hint
- reported_date

Rules:
- Only Northern Pakistan roads
- If none, return []
Text:
"""

# -------------------------
# RULE-BASED EXTRACTION (FAST + FREE)
# -------------------------
def rule_extract(content: str):
    text = content.lower()

    keywords = [
        "road", "highway", "pass", "blocked",
        "closure", "landslide", "snow",
        "gilgit", "hunza", "skardu", "kkh",
        "naran", "babusar", "chilas"
    ]

    if not any(k in text for k in keywords):
        return None

    event_type = "advisory"

    if "landslide" in text:
        event_type = "landslide"
    elif "snow" in text:
        event_type = "snow"
    elif "blocked" in text or "closed" in text:
        event_type = "closure"
    elif "open" in text:
        event_type = "open"
    elif "checkpoint" in text:
        event_type = "checkpoint"

    return [{
        "route_name": "Unknown Route",
        "event_type": event_type,
        "description": content[:300],
        "location_hint": "unknown",
        "reported_date": "unknown"
    }]


# -------------------------
# GEMINI CALL (SAFE)
# -------------------------
def safe_gemini_call(prompt):
    global GEMINI_QUOTA_EXHAUSTED

    if GEMINI_QUOTA_EXHAUSTED:
        return None

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text.strip()

    except Exception as e:
        msg = str(e).lower()

        if "429" in msg or "quota" in msg or "exceeded" in msg:
            print("[Gemini] QUOTA EXHAUSTED")
            GEMINI_QUOTA_EXHAUSTED = True
            return None

        print(f"[Gemini Error] {e}")
        return None


# -------------------------
# MAIN WORKER
# -------------------------
def run_extraction():
    print("[Extraction] Starting...")

    scrapes = get_unprocessed_scrapes()[:10]  # limit batch size
    print(f"[Extraction] {len(scrapes)} items to process")

    for scrape in scrapes:

        scrape_id = scrape["id"]
        source_name = scrape.get("source_name", "unknown")
        source_url = scrape.get("source_url", "")
        content = scrape.get("content", "")[:2500]  # IMPORTANT quota saver

        print(f"[Extraction] Processing from {source_name}...")
        time.sleep(2)

        # -------------------------
        # STEP 1: RULE ENGINE (FREE)
        # -------------------------
        events = rule_extract(content)

        # -------------------------
        # STEP 2: GEMINI FALLBACK
        # -------------------------
        if events is None:

            raw = safe_gemini_call(PROMPT + content)

            if raw is None:
                print("[Extraction] Skipping (Gemini failed)")
                mark_scrape_processed(scrape_id)
                continue

            raw = raw.replace("```json", "").replace("```", "").strip()

            try:
                events = json.loads(raw)
            except:
                print("[Extraction] Invalid JSON")
                mark_scrape_processed(scrape_id)
                continue

        # -------------------------
        # VALIDATE
        # -------------------------
        if not isinstance(events, list):
            mark_scrape_processed(scrape_id)
            continue

        print(f"[Extraction] Found {len(events)} events")

        # -------------------------
        # SAVE EVENTS
        # -------------------------
        for event in events:

            if not isinstance(event, dict):
                continue

            if "route_name" not in event or "event_type" not in event:
                continue

            save_event(
                route_name=event.get("route_name", "Unknown"),
                event_type=event.get("event_type", "advisory"),
                description=event.get("description", ""),
                location_hint=event.get("location_hint", "unknown"),
                reported_date=None if event.get("reported_date") in ["unknown", "", None] else event.get("reported_date"),
                source_url=source_url,
                source_name=source_name
)

        # mark done
        mark_scrape_processed(scrape_id)

    print("[Extraction] Done")


if __name__ == "__main__":
    run_extraction()