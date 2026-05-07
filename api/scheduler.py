from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.dawn_scraper import scrape_dawn
from scrapers.tribune_scraper import scrape_tribune
from scrapers.ndma_scraper import scrape_ndma
from scrapers.pmd_scraper import scrape_pmd
from scrapers.facebook_scraper import scrape_facebook
from workers.extraction_worker import run_extraction


def run_pipeline():
    print("\n===== PIPELINE STARTING =====")
    scrape_dawn()
    scrape_tribune()
    scrape_ndma()
    scrape_pmd()
    scrape_facebook()
    print("--- Scraping done. Running extraction... ---")
    run_extraction()
    print("===== PIPELINE COMPLETE =====\n")


if __name__ == "__main__":
    print("RouteAware Scheduler starting...")
    run_pipeline()  # Run once immediately

    scheduler = BlockingScheduler()
    scheduler.add_job(
        run_pipeline,
        trigger=IntervalTrigger(minutes=30),
        id="pipeline",
        replace_existing=True
    )
    print("Scheduler running every 30 minutes. Press Ctrl+C to stop.")
    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("Stopped.")