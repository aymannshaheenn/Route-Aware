import threading
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from database import supabase
from planner import generate_trip_plan

app = FastAPI(title="RouteAware API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def run_confidence_scoring():
    """Runs confidence scoring in the background."""
    try:
        from confidence import compute_all_scores
        compute_all_scores()
        print("Confidence scores updated.")
    except Exception as e:
        print(f"Confidence scoring error: {e}")

# Start background scheduler when API starts
scheduler = BackgroundScheduler()
scheduler.add_job(run_confidence_scoring, 'interval', minutes=10)
scheduler.start()

# Run once immediately on startup
threading.Thread(target=run_confidence_scoring).start()

# ─── ROOT ────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "RouteAware API running"}

# ─── TEAMMATE A: RAW EVENTS ──────────────────────────────────────────────────

@app.get("/api/events")
def get_events(limit: int = 100):
    try:
        result = supabase.table("events") \
            .select("*") \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()
        return {"events": result.data, "count": len(result.data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/events/route/{route_name}")
def get_events_by_route(route_name: str):
    try:
        result = supabase.table("events") \
            .select("*") \
            .ilike("route_name", f"%{route_name}%") \
            .order("created_at", desc=True) \
            .limit(20) \
            .execute()
        return {"events": result.data, "route": route_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
def get_stats():
    try:
        scrapes = supabase.table("raw_scrapes").select("id", count="exact").execute()
        events = supabase.table("events").select("id", count="exact").execute()
        return {
            "total_scrapes": scrapes.count,
            "total_events": events.count,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─── ABDULLAH: CONFIDENCE SCORES ─────────────────────────────────────────────

@app.get("/api/segments")
def get_all_segments():
    try:
        routes_response = supabase.table("routes").select("*").execute()
        routes = routes_response.data

        confidence_response = supabase.table("route_confidence").select("*").execute()
        confidence_data = confidence_response.data

        confidence_lookup = {}
        for item in confidence_data:
            route_id = item["route_id"]
            if route_id not in confidence_lookup:
                confidence_lookup[route_id] = item
            else:
                if item["last_computed"] > confidence_lookup[route_id]["last_computed"]:
                    confidence_lookup[route_id] = item

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

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/segments/{route_id}")
def get_single_segment(route_id: int):
    try:
        route_response = supabase.table("routes") \
            .select("*") \
            .eq("id", route_id) \
            .execute()

        if not route_response.data:
            raise HTTPException(status_code=404, detail="Route not found")

        route = route_response.data[0]

        confidence_response = supabase.table("route_confidence") \
            .select("*") \
            .eq("route_id", route_id) \
            .order("last_computed", desc=True) \
            .limit(1) \
            .execute()

        confidence = confidence_response.data[0] if confidence_response.data else None

        events_response = supabase.table("events") \
            .select("*") \
            .eq("route_id", route_id) \
            .order("reported_at", desc=True) \
            .execute()

        return {
            "id": route["id"],
            "name": route["name"],
            "from_place": route["from_place"],
            "to_place": route["to_place"],
            "start_lat": route.get("start_lat"),
            "start_lng": route.get("start_lng"),
            "end_lat": route.get("end_lat"),
            "end_lng": route.get("end_lng"),
            "confidence_score": confidence["confidence_score"] if confidence else 0.5,
            "color": confidence["color"] if confidence else "gray",
            "last_computed": confidence["last_computed"] if confidence else None,
            "events": events_response.data
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─── ABDULLAH: TRIP PLANNER ──────────────────────────────────────────────────

@app.get("/api/plan")
def plan_trip(origin: str, destination: str, days: int = 3):
    try:
        result = generate_trip_plan(origin, destination, days)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)