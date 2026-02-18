import logging
import sys
import os

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scanner import Scanner
from scrapers.cvpr import CVPRScraper
from database import SessionLocal, init_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dry_run")

def dry_run():
    logger.info("Initializing DB...")
    init_db()
    session = SessionLocal()
    
    # Target CVPR 2024 (Static, fast)
    url = "https://openaccess.thecvf.com/CVPR2024?day=all"
    logger.info(f"Scraping small batch from {url}...")
    
    scraper = CVPRScraper("CVPR", 2024)
    # Scrape papers (this gets all of them, but we will only save 5)
    # Note: scraping CVPR 2024 static page is fast enough (requests)
    papers = scraper.scrape(url)
    
    if not papers:
        logger.error("❌ Failed to scrape any papers!")
        sys.exit(1)
        
    logger.info(f"Scraper found {len(papers)} papers (fetching complete).")
    logger.info("Attempting to save FIRST 5 papers to DB...")
    
    scanner = Scanner()
    saved_count = 0
    
    for i, p in enumerate(papers[:5]):
        logger.info(f"Saving: {p.title}")
        if scanner._save_paper(session, p, "CVPR", 2024, url):
            saved_count += 1
            
    session.commit()
    session.close()
    
    logger.info(f"✅ Dry Run Successful! Saved/Processed {saved_count} papers.")
    logger.info("Database connection and Write permissions are good.")

if __name__ == "__main__":
    dry_run()
