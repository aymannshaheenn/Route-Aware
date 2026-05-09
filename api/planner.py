import os
from dotenv import load_dotenv
from groq import Groq
from database import supabase

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_route_conditions():
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

    conditions = []
    for route in routes:
        route_id = route["id"]
        confidence = confidence_lookup.get(route_id)

        if not confidence:
            status = "UNKNOWN - no data available"
            color = "gray"
            score = 0.5
        elif confidence["color"] == "red":
            status = "DANGEROUS - active hazard reported"
            color = "red"
            score = confidence["confidence_score"]
        elif confidence["color"] == "yellow":
            status = "CAUTION - some risk reported"
            color = "yellow"
            score = confidence["confidence_score"]
        elif confidence["color"] == "green":
            status = "SAFE - no hazards reported"
            color = "green"
            score = confidence["confidence_score"]
        else:
            status = "UNKNOWN - no data available"
            color = "gray"
            score = 0.5

        conditions.append({
            "route": route["name"],
            "from": route["from_place"],
            "to": route["to_place"],
            "status": status,
            "color": color,
            "confidence_score": score
        })

    return conditions


def generate_trip_plan(origin: str, destination: str, days: int):
    conditions = get_route_conditions()

    conditions_text = ""
    for c in conditions:
        conditions_text += f"- {c['route']}: {c['status']} (score: {c['confidence_score']:.2f})\n"

    system_prompt = f"""You are RouteAware, an honest travel planning AI for Pakistan's Northern Areas.

CRITICAL RULES YOU MUST FOLLOW:
1. You can ONLY reference road conditions from the data provided below
2. You CANNOT invent or assume road conditions not in the data
3. If a road is marked DANGEROUS, you MUST warn the user and suggest alternatives
4. If a road is marked UNKNOWN, you MUST tell the user you don't have data and they should verify
5. Never say a road is safe if the data says otherwise

CURRENT ROAD CONDITIONS (real-time data):
{conditions_text}

Your response must include:
- A day-by-day itinerary
- Clear warnings for any dangerous roads
- Alternative routes when primary route is dangerous
- Honest disclosure when you don't have data
- Practical advice (fuel stops, accommodation, timing)"""

    user_message = f"""Plan a {days}-day trip from {origin} to {destination} in Pakistan's Northern Areas.

Give me:
1. Recommended route with honest road condition warnings
2. Day by day breakdown
3. Roads to avoid and why
4. Alternative routes if main route has hazards
5. Key stops, fuel stations, and accommodation"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=2000
        )
        return {
            "success": True,
            "plan": response.choices[0].message.content,
            "road_conditions": conditions
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "road_conditions": conditions
        }