import os
import math
from datetime import datetime, timezone
from dotenv import load_dotenv
from supabase import create_client, Client
from apscheduler.schedulers.blocking import BlockingScheduler

# Load environment variables from .env file
load_dotenv()

# Connect to Supabase
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Severity weights — how serious each event type is
SEVERITY_WEIGHTS = {
    "landslide": 0.9,
    "closure": 0.8,
    "snow": 0.6,
    "weather_warning": 0.4,
    "advisory": 0.2,
    "open": 0.0  # open road is good, no negative impact
}

def get_hours_since(reported_at_str):
    """Calculate how many hours ago an event was reported."""
    reported_at = datetime.fromisoformat(
        reported_at_str.replace("Z", "")
    )
    now = datetime.utcnow()
    diff = now - reported_at
    hours = diff.total_seconds() / 3600
    return hours

def compute_segment_confidence(route_id):
    """
    Compute a confidence score for a single route segment.
    
    Score meaning:
    - 0.7 to 1.0 = GREEN (safe, recent data)
    - 0.4 to 0.69 = YELLOW (caution, some risk or old data)
    - 0.0 to 0.39 = RED (danger or blocked)
    - 0.5 (default) = GRAY (no data available)
    """
    
    # Fetch all events for this route from the last 7 days
    response = supabase.table("events")\
        .select("*")\
        .eq("route_id", route_id)\
        .execute()
    
    events = response.data
    
    # If no events found, return unknown state
    if not events:
        return 0.5, "gray"
    
    # Calculate weighted score from all events
    total_score = 0.0
    unique_sources = set()
    
    for event in events:
        event_type = event.get("event_type", "advisory")
        reported_at = event.get("reported_at")
        source_name = event.get("source_name", "unknown")
        
        # Track unique sources for diversity bonus
        unique_sources.add(source_name)
        
        # Get severity weight for this event type
        severity = SEVERITY_WEIGHTS.get(event_type, 0.3)
        
        # Skip open road events — they don't add danger
        if event_type == "open":
            continue
        
        # Calculate time decay
        # Events older than 48 hours decay exponentially
        if reported_at:
            hours_ago = get_hours_since(reported_at)
        else:
            hours_ago = 24  # assume 24 hours if no date
            
        time_decay = math.exp(-0.05 * hours_ago)
        
        # Final weight for this event
        event_score = severity * time_decay
        total_score += event_score
    
    # Apply source diversity bonus
    # More unique sources = more trustworthy
    diversity_bonus = 1 + (0.1 * len(unique_sources))
    total_score = total_score * diversity_bonus
    
    # Cap at 1.0
    total_score = min(total_score, 1.0)
    
    # Assign color based on score
    if total_score >= 0.7:
        color = "red"    # high danger score = red on map
    elif total_score >= 0.4:
        color = "yellow" # medium danger = yellow
    elif total_score > 0:
        color = "green"  # low danger = green
    else:
        color = "green"  # no dangerous events = green
    
    return total_score, color

def compute_all_scores():
    """
    Compute confidence scores for ALL routes and save to database.
    This runs every 10 minutes automatically.
    """
    print(f"Computing scores for all routes... {datetime.now()}")
    
    # Fetch all routes
    routes_response = supabase.table("routes").select("*").execute()
    routes = routes_response.data
    
    for route in routes:
        route_id = route["id"]
        route_name = route["name"]
        
        # Compute score for this route
        score, color = compute_segment_confidence(route_id)
        
        print(f"Route: {route_name} → Score: {score:.2f} → {color}")
        
        # Save to route_confidence table
        # Check if a record already exists for this route
        existing = supabase.table("route_confidence")\
            .select("*")\
            .eq("route_id", route_id)\
            .execute()
        
        if existing.data:
            # Update existing record
            supabase.table("route_confidence")\
                .update({
                    "confidence_score": score,
                    "color": color,
                    "last_computed": datetime.now(timezone.utc).isoformat()
                })\
                .eq("route_id", route_id)\
                .execute()
        else:
            # Insert new record
            supabase.table("route_confidence")\
                .insert({
                    "route_id": route_id,
                    "confidence_score": score,
                    "color": color,
                    "last_computed": datetime.now(timezone.utc).isoformat()
                })\
                .execute()
    
    print("All scores updated successfully.")

# Run once immediately when script starts
compute_all_scores()

# Then schedule to run every 10 minutes
scheduler = BlockingScheduler()
scheduler.add_job(compute_all_scores, 'interval', minutes=10)
print("Scheduler started. Running every 10 minutes...")
scheduler.start()