from scrapers.cvpr import CVPRScraper
from playwright.sync_api import sync_playwright
import logging

logging.basicConfig(level=logging.INFO)

def debug_cvpr_2025():
    url = "https://cvpr.thecvf.com/Conferences/2025/AcceptedPapers"
    print(f"Debugging {url}...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        
        # Wait for load
        page.wait_for_load_state("networkidle")
        
        # Scroll once
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(2000)
        
        # Take screenshot
        page.screenshot(path="cvpr_debug.png", full_page=False)
        
        # Save HTML
        with open("cvpr_debug.html", "w") as f:
            f.write(page.content())
            
    print("Saved cvpr_debug.png and cvpr_debug.html")

if __name__ == "__main__":
    debug_cvpr_2025()
