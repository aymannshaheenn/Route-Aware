import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import save_event

EVENTS = [
    # Karakoram Highway
    ("Karakoram Highway", "open", "KKH fully open between Gilgit and Hunza. Good road conditions reported by travelers.", "Gilgit to Hunza", "2026-05-05", "https://www.dawn.com", "dawn"),
    ("Karakoram Highway", "landslide", "Landslide near Raikot Bridge blocks one lane. NHMP on site, clearance expected in 6 hours.", "Raikot Bridge, near Chilas", "2026-04-28", "https://www.dawn.com", "dawn"),
    ("Karakoram Highway", "open", "KKH clear between Mansehra and Chilas. Normal traffic flow reported.", "Mansehra to Chilas", "2026-05-04", "https://tribune.com.pk", "tribune"),
    ("Karakoram Highway", "advisory", "Slow moving traffic near Besham due to construction. Expect 45 minute delay.", "Besham", "2026-05-03", "https://www.geo.tv", "geo"),
    ("Karakoram Highway", "landslide", "Fresh landslide reported between Gilgit and Chilas. Road partially blocked.", "Between Gilgit and Chilas", "2026-04-15", "https://ndma.gov.pk", "ndma"),
    ("Karakoram Highway", "open", "KKH Hunza to Sost fully open. Chinese border at Khunjerab operational.", "Hunza to Sost", "2026-05-01", "https://tribune.com.pk", "tribune"),
    ("Karakoram Highway", "weather_warning", "Heavy rain forecast for KKH corridor. PMD advises caution near Gilgit.", "Gilgit stretch", "2026-04-30", "https://www.pmd.gov.pk", "pmd"),
    ("Karakoram Highway", "closure", "KKH closed near Dasu due to flooding. Alternative route via Shangla advised.", "Dasu, Kohistan", "2025-08-12", "https://ndma.gov.pk", "ndma"),

    # Babusar Pass
    ("Babusar Pass", "closure", "Babusar Pass officially closed due to heavy snowfall. NHMP has blocked entry at Naran.", "Babusar Top", "2025-11-20", "https://ndma.gov.pk", "ndma"),
    ("Babusar Pass", "open", "Babusar Pass reopened after winter closure. Road cleared by NHA. Travelers advised to check conditions.", "Babusar Top", "2026-04-10", "https://www.dawn.com", "dawn"),
    ("Babusar Pass", "advisory", "Babusar Pass open but snow patches remain. 4x4 vehicles recommended. Drive carefully.", "Near Babusar Top", "2026-04-20", "https://tribune.com.pk", "tribune"),
    ("Babusar Pass", "weather_warning", "PMD warns of snowfall above 3000m. Babusar Pass travelers should monitor conditions.", "Babusar Pass area", "2026-04-25", "https://www.pmd.gov.pk", "pmd"),
    ("Babusar Pass", "open", "Road from Naran to Babusar fully passable. Clear weather reported by travelers today.", "Naran to Babusar", "2026-05-05", "https://tribune.com.pk", "tribune"),

    # Naran Road
    ("Naran-Babusar Road", "open", "Naran Valley road fully open. Tourist season underway with heavy traffic on weekends.", "Balakot to Naran", "2026-05-04", "https://www.geo.tv", "geo"),
    ("Naran-Babusar Road", "weather_warning", "Flash flood risk in Kunhar River area. PMD advises travelers to avoid river crossings.", "Naran Valley", "2026-05-02", "https://www.pmd.gov.pk", "pmd"),
    ("Naran-Babusar Road", "closure", "Road blocked near Kaghan due to flash flooding. NHA teams deployed.", "Kaghan", "2025-07-28", "https://ndma.gov.pk", "ndma"),

    # Skardu Road
    ("Skardu Road", "open", "Gilgit-Skardu road fully operational. Smooth traffic reported on entire stretch.", "Gilgit to Skardu", "2026-05-05", "https://www.dawn.com", "dawn"),
    ("Skardu Road", "advisory", "Road work ongoing between Skardu and Shigar. One lane traffic, expect 30 min delays.", "Skardu-Shigar junction", "2026-04-20", "https://ndma.gov.pk", "ndma"),
    ("Skardu Road", "landslide", "Small landslide near Rondu blocks one lane. Manual clearing underway.", "Rondu, Skardu road", "2026-04-18", "https://tribune.com.pk", "tribune"),
    ("Skardu Road", "open", "Skardu airport road and main bazaar road clear. No issues reported.", "Skardu city", "2026-05-03", "https://www.geo.tv", "geo"),

    # Khunjerab Pass
    ("Khunjerab Pass", "checkpoint", "Khunjerab Pass open for Pakistani nationals. Foreign tourists require NOC from Ministry of Interior.", "Sost border checkpoint", "2026-04-15", "https://www.dawn.com", "dawn"),
    ("Khunjerab Pass", "open", "Pass fully open. China-Pakistan border trade resumed for the season.", "Khunjerab Top", "2026-05-01", "https://tribune.com.pk", "tribune"),
    ("Khunjerab Pass", "closure", "Khunjerab closed due to blizzard. Expected to reopen in 48 hours.", "Khunjerab Pass", "2025-12-05", "https://ndma.gov.pk", "ndma"),

    # Chitral Road
    ("Chitral Road", "landslide", "Multiple small landslides on Lowari Pass approach after heavy rain. Clearance underway.", "Lowari Pass, Dir District", "2026-04-10", "https://www.geo.tv", "geo"),
    ("Chitral Road", "open", "Lowari Tunnel open. Chitral accessible via tunnel. No need for Lowari Top in winter.", "Lowari Tunnel", "2026-05-04", "https://www.dawn.com", "dawn"),
    ("Chitral Road", "advisory", "Chitral-Booni road under repair. Slow traffic near Mastuj.", "Mastuj, Chitral", "2026-04-22", "https://tribune.com.pk", "tribune"),
    ("Chitral Road", "weather_warning", "Heavy rain warning for Chitral district. River levels rising near Dir.", "Dir to Chitral", "2026-05-02", "https://www.pmd.gov.pk", "pmd"),

    # Swat
    ("Swat Expressway", "open", "Swat Expressway fully operational. Travel time from Peshawar to Mingora approximately 2 hours.", "Peshawar to Mingora", "2026-05-01", "https://tribune.com.pk", "tribune"),
    ("Swat Expressway", "open", "Expressway clear with no incidents. Heavy tourist traffic expected this weekend.", "Full expressway", "2026-05-05", "https://www.dawn.com", "dawn"),
    ("Swat Valley Road", "open", "Kalam road open. Travelers reporting good conditions from Mingora to Kalam.", "Mingora to Kalam", "2026-05-03", "https://www.geo.tv", "geo"),
    ("Swat Valley Road", "advisory", "Road resurfacing between Madyan and Bahrain. Single lane traffic in sections.", "Madyan to Bahrain", "2026-04-28", "https://tribune.com.pk", "tribune"),

    # Astore Road
    ("Astore Road", "advisory", "Single lane traffic due to maintenance between Gilgit and Astore junction.", "Astore Valley entry", "2026-04-25", "https://ndma.gov.pk", "ndma"),
    ("Astore Road", "open", "Astore road fully open. Route to Rama Lake accessible. Good conditions reported.", "Astore to Rama", "2026-05-04", "https://www.dawn.com", "dawn"),

    # Hunza Valley
    ("Hunza Valley Road", "open", "Karimabad and Aliabad roads fully clear. Tourist facilities open for season.", "Karimabad, Hunza", "2026-05-05", "https://tribune.com.pk", "tribune"),
    ("Hunza Valley Road", "advisory", "Attabad Lake tunnel stretch under monitoring after minor crack reported. Safe to pass.", "Attabad Lake tunnel", "2026-04-29", "https://ndma.gov.pk", "ndma"),

    # Gilgit City
    ("Gilgit City Roads", "open", "All main roads in Gilgit city operational. Airport road clear.", "Gilgit city", "2026-05-05", "https://www.geo.tv", "geo"),
    ("Gilgit City Roads", "advisory", "Bridge maintenance on Gilgit River bridge. Alternate route via KKH bridge available.", "Gilgit River bridge", "2026-04-26", "https://ndma.gov.pk", "ndma"),

    # General Northern Pakistan
    ("Karakoram Highway", "open", "Overall KKH conditions good for the season. NHA completed winter maintenance.", "Full KKH stretch", "2026-04-05", "https://www.dawn.com", "dawn"),
    ("Babusar Pass", "advisory", "Early season travelers on Babusar advised to carry chains and travel in convoy.", "Babusar Pass", "2026-04-12", "https://tribune.com.pk", "tribune"),
    ("Skardu Road", "open", "Flights and road to Skardu both operational. No weather disruption this week.", "Skardu", "2026-05-05", "https://www.geo.tv", "geo"),
    ("Chitral Road", "open", "Chitral fully accessible via Lowari Tunnel. Road conditions good.", "Chitral", "2026-05-05", "https://www.dawn.com", "dawn"),
]


def seed():
    print(f"Seeding {len(EVENTS)} events into database...")
    success = 0
    for e in EVENTS:
        try:
            save_event(
                route_name=e[0], event_type=e[1], description=e[2],
                location_hint=e[3], reported_date=e[4],
                source_url=e[5], source_name=e[6]
            )
            success += 1
        except Exception as err:
            print(f"Failed to save: {e[0]} — {err}")
    print(f"Done! {success}/{len(EVENTS)} events saved.")
    print("Check Supabase → events table now.")


if __name__ == "__main__":
    seed()