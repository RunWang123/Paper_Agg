import logging
import sqlite3
from scrapers.cvpr import CVPRScraper
from database import Paper

# Setup simple logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_cvpr_scraper():
    print("🔍 Testing CVPR 2025 Scraper...")
    
    url = "https://cvpr.thecvf.com/Conferences/2025/AcceptedPapers"
    scraper = CVPRScraper("CVPR", 2025)
    
    # 1. Run the scraper logic in memory
    print(f"📡 Fetching papers from {url}...")
    found_papers = scraper.scrape(url)
    print(f"✅ Scraper found {len(found_papers)} papers.")
    
    # DEBUG: Print first 20 and last 20 titles to see what we are getting
    # and search for "Visual Geometry Grounded Transformer" specifically
    found_titles = [p.title for p in found_papers]
    
    print("\n--- SAMPLE TITLES ---")
    for t in found_titles[:5]: print(f"  - {t}")
    print("...")
    for t in found_titles[-5:]: print(f"  - {t}")
    
    # 2. Check for specific paper "VGGT"
    vggt_found = False
    for p in found_papers:
        # Check title loosely
        if "VGGT" in p.title or "Visual Geometry Grounded Transformer" in p.title:
            vggt_found = True
            print(f"\n🎯 FOUND TARGET PAPER:")
            print(f"   Title: {p.title}")
            print(f"   URL:   {p.url}")
            print(f"   Auth:  {p.authors}")
            break

            
    if not vggt_found:
        print("\n❌ VGGT paper was NOT found by the scraper.")
    
    # 3. Compare with Local DB (if exists)
    db_path = "./database/papers.db"
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"\n💾 Checking Local Database ({db_path})...")
        
        # Check if VGGT is in DB
        cursor.execute("SELECT title, url FROM papers WHERE title LIKE '%VGGT%'")
        existing = cursor.fetchone()
        
        if existing:
            print(f"✅ VGGT is ALREADY in the database: {existing[0]}")
        else:
            print(f"⚠️  VGGT is NOT in the database yet.")
            
        # Count total CVPR 2025 in DB
        cursor.execute("SELECT count(*) FROM papers WHERE conference = 'CVPR' AND year = 2025")
        count = cursor.fetchone()[0]
        print(f"📊 Total CVPR 2025 papers in DB: {count}")
        
        conn.close()
        
    except Exception as e:
        print(f"⚠️  Could not check local DB: {e}")

if __name__ == "__main__":
    check_cvpr_scraper()
