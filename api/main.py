from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import supabase

app = FastAPI(title="RouteAware API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "RouteAware API running"}


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)