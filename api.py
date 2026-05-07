import os
from dotenv import load_dotenv
from supabase import create_client, Client
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()

# Connect to Supabase
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Create the FastAPI app
app = FastAPI()

# CORS — this allows your frontend (Next.js) to call this API
# Without this, the browser will block the requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    """Health check — visiting this URL confirms the server is running."""
    return {"status": "RouteAware API is running"}

@app.get("/api/segments")
def get_all_segments():
    """
    Returns all route segments with their current confidence scores.
    The frontend uses this to draw colored roads on the map.
    """
    
    # Fetch all routes
    routes_response = supabase.table("routes")\
        .select("*")\
        .execute()
    routes = routes_response.data
    
    # Fetch all confidence scores
    confidence_response = supabase.table("route_confidence")\
        .select("*")\
        .execute()
    confidence_data = confidence_response.data
    
    # Create a lookup dictionary for confidence scores
    # key = route_id, value = confidence data
    confidence_lookup = {}
    for item in confidence_data:
        route_id = item["route_id"]
        # Keep the most recently computed score for each route
        if route_id not in confidence_lookup:
            confidence_lookup[route_id] = item
        else:
            existing = confidence_lookup[route_id]["last_computed"]
            current = item["last_computed"]
            if current > existing:
                confidence_lookup[route_id] = item
    
    # Combine routes with their confidence scores
    result = []
    for route in routes:
        route_id = route["id"]
        confidence = confidence_lookup.get(route_id)
        
        result.append({
            "id": route_id,
            "name": route["name"],
            "from_place": route["from_place"],
            "to_place": route["to_place"],
            "start_lat": route.get("start_lat"),
            "start_lng": route.get("start_lng"),
            "end_lat": route.get("end_lat"),
            "end_lng": route.get("end_lng"),
            "confidence_score": confidence["confidence_score"] if confidence else 0.5,
            "color": confidence["color"] if confidence else "gray",
            "last_computed": confidence["last_computed"] if confidence else None
        })
    
    return {"segments": result}

@app.get("/api/segments/{route_id}")
def get_single_segment(route_id: int):
    """
    Returns one specific route segment with all its events.
    The frontend calls this when a user taps a road on the map.
    """
    
    # Fetch the route
    route_response = supabase.table("routes")\
        .select("*")\
        .eq("id", route_id)\
        .execute()
    
    if not route_response.data:
        return {"error": "Route not found"}
    
    route = route_response.data[0]
    
    # Fetch confidence score for this route
    confidence_response = supabase.table("route_confidence")\
        .select("*")\
        .eq("route_id", route_id)\
        .order("last_computed", desc=True)\
        .limit(1)\
        .execute()
    
    confidence = confidence_response.data[0] if confidence_response.data else None
    
    # Fetch all events for this route
    events_response = supabase.table("events")\
        .select("*")\
        .eq("route_id", route_id)\
        .order("reported_at", desc=True)\
        .execute()
    
    events = events_response.data
    
    return {
        "id": route["id"],
        "name": route["name"],
        "from_place": route["from_place"],
        "to_place": route["to_place"],
        "confidence_score": confidence["confidence_score"] if confidence else 0.5,
        "color": confidence["color"] if confidence else "gray",
        "last_computed": confidence["last_computed"] if confidence else None,
        "events": events
    }