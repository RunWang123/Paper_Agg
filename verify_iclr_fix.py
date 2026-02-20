from scrapers.iclr import ICLRScraper

def verify_fix():
    print("Verifying ICLR 2024...")
    scraper = ICLRScraper("ICLR", 2024)
    # URL argument is ignored by the JSON logic but required by interface
    papers = scraper.scrape("https://iclr.cc/virtual/2024/papers.html")
    
    print(f"Total Papers: {len(papers)}")
    
    # Check Tracks
    orals = [p for p in papers if p.tags and "Oral" in p.tags]
    print(f"Oral Papers: {len(orals)}")
    
    # Check PDF
    pdfs = [p for p in papers if p.pdf_url]
    print(f"Papers with PDF URL: {len(pdfs)}")
    
    if len(papers) > 2300 and len(orals) > 100:
        print("SUCCESS: JSON Scraper is working correctly!")
    else:
        print("FAILURE: Stats look wrong.")

if __name__ == "__main__":
    verify_fix()
