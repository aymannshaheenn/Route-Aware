import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)


def save_raw_scrape(source_name: str, source_url: str, content: str):
    try:
        supabase.table("raw_scrapes").insert({
            "source_name": source_name,
            "source_url": source_url,
            "content": content,
            "processed": False
        }).execute()
        print(f"[DB] Saved scrape from {source_name}")
    except Exception as e:
        print(f"[DB ERROR] {e}")


def get_unprocessed_scrapes():
    try:
        result = supabase.table("raw_scrapes") \
            .select("*") \
            .eq("processed", False) \
            .limit(10) \
            .execute()
        return result.data
    except Exception as e:
        print(f"[DB ERROR] {e}")
        return []


def save_event(route_name, event_type, description,
               location_hint, reported_date, source_url, source_name):
    try:
        supabase.table("events").insert({
            "route_name": route_name,
            "event_type": event_type,
            "description": description,
            "location_hint": location_hint,
            "reported_date": reported_date if reported_date else None,
            "source_url": source_url,
            "source_name": source_name,
            "confidence_weight": 0.6
        }).execute()
        print(f"[DB] Saved event: {event_type} on {route_name}")
    except Exception as e:
        print(f"[DB ERROR] {e}")


def mark_scrape_processed(scrape_id: str):
    try:
        supabase.table("raw_scrapes") \
            .update({"processed": True}) \
            .eq("id", scrape_id) \
            .execute()
    except Exception as e:
        print(f"[DB ERROR] mark processed: {e}")