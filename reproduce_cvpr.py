from scrapers.cvpr import CVPRScraper
import logging

logging.basicConfig(level=logging.INFO)

def test_cvpr_2025():
    scraper = CVPRScraper("CVPR", 2025)
    url = "https://cvpr.thecvf.com/Conferences/2025/AcceptedPapers"
    print(f"Scraping {url}...")
    papers = scraper.scrape(url)
    print(f"Found {len(papers)} papers.")
    
    # Count how many have real links (potential for abstract) vs placeholders
    real_links = [p for p in papers if "#" not in p.url or "cvpr.thecvf.com" not in p.url] 
    # Actually, my placeholder logic was url + "#" + slug.
    # Real links might be to openaccess, arxiv, project page, etc.
    # The placeholder ones are strictly the ones we generated.
    
    # Let's count how many are just the base URL + #
    placeholders = [p for p in papers if p.url.startswith(url + "#")]
    real_count = len(papers) - len(placeholders)
    
    print(f"Papers with exploitable links: {real_count}")
    print(f"Papers with NO links (placeholders): {len(placeholders)}")
    
    if len(placeholders) > 0:
        print(f"Sample placeholder: {placeholders[0]}")
    
    # Check if we have abstracts (should be None initially as scrape() doesn't fetch them)
    print(f"Sample paper: {papers[0] if papers else 'None'}")

if __name__ == "__main__":
    test_cvpr_2025()
