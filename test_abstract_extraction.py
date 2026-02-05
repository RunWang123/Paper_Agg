#!/usr/bin/env python3
"""
Comprehensive test for abstract extraction across ALL conferences.
"""

import sys
sys.path.insert(0, '.')

from scrapers.cvpr import CVPRScraper
from scrapers.iccv import ICCVScraper
from scrapers.eccv import ECCVScraper
from scrapers.neurips import NeurIPSScraper
from scrapers.icml import ICMLScraper
from scrapers.iclr import ICLRScraper
from scrapers.ndss import NDSSScraper
from scrapers.usenix_security import USENIXScraper
from scrapers.ieee_sp import IEEESPScraper
from scrapers.acm_ccs import ACMCCSScraper
import warnings
warnings.filterwarnings('ignore')


def test_all_conferences():
    """Test abstract extraction for all configured conferences."""
    
    tests = [
        # Computer Vision
        {"name": "CVPR 2023", "scraper": CVPRScraper("CVPR", 2023), 
         "url": "https://openaccess.thecvf.com/CVPR2023?day=all"},
        {"name": "ECCV 2022", "scraper": ECCVScraper("ECCV", 2022), 
         "url": "https://www.ecva.net/papers.php"},
        
        # Machine Learning
        {"name": "NeurIPS 2023", "scraper": NeurIPSScraper("NeurIPS", 2023), 
         "url": "https://papers.nips.cc/paper_files/paper/2023"},
        {"name": "ICML 2023", "scraper": ICMLScraper("ICML", 2023), 
         "url": "https://icml.cc/virtual/2023/papers.html"},
        {"name": "ICLR 2023", "scraper": ICLRScraper("ICLR", 2023), 
         "url": "https://iclr.cc/virtual/2023/papers.html"},
        
        # Security
        {"name": "NDSS 2024", "scraper": NDSSScraper("NDSS", 2024), 
         "url": "https://dblp.org/db/conf/ndss/ndss2024.html"},
        {"name": "USENIX 2024", "scraper": USENIXScraper("USENIX", 2024), 
         "url": "https://dblp.org/db/conf/uss/uss2024.html"},
        {"name": "IEEE S&P 2024", "scraper": IEEESPScraper("IEEESP", 2024), 
         "url": "https://dblp.org/db/conf/sp/sp2024.html"},
        {"name": "ACM CCS 2024", "scraper": ACMCCSScraper("ACMCCS", 2024), 
         "url": "https://dblp.org/db/conf/ccs/ccs2024.html"},
    ]
    
    print("=" * 80)
    print("COMPREHENSIVE ABSTRACT EXTRACTION TEST - ALL CONFERENCES")
    print("=" * 80)
    
    results = []
    
    for test in tests:
        print(f"\n{'='*40}")
        print(f"📄 {test['name']}")
        print(f"   URL: {test['url'][:55]}...")
        
        try:
            # Step 1: Scrape papers list
            papers = test['scraper'].scrape(test['url'])
            print(f"   📚 Found {len(papers)} papers")
            
            if len(papers) == 0:
                print("   ⚠️  No papers found - skipping abstract test")
                results.append({"name": test['name'], "papers": 0, "abstract": "N/A", "status": "NO PAPERS"})
                continue
            
            # Step 2: Test abstract extraction on first paper
            paper = papers[0]
            print(f"   📝 Testing: {paper.title[:50]}...")
            print(f"   🔗 Paper URL: {paper.url[:60]}...")
            
            abstract = test['scraper'].scrape_abstract(paper.url)
            
            if abstract and len(abstract) > 50:
                print(f"   ✅ SUCCESS! Abstract found ({len(abstract)} chars)")
                print(f"   📖 Preview: {abstract[:120]}...")
                results.append({"name": test['name'], "papers": len(papers), "abstract": len(abstract), "status": "SUCCESS"})
            else:
                print(f"   ❌ FAILED - No abstract found")
                results.append({"name": test['name'], "papers": len(papers), "abstract": 0, "status": "FAILED"})
                
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)[:100]}")
            results.append({"name": test['name'], "papers": 0, "abstract": 0, "status": f"ERROR: {str(e)[:50]}"})
    
    # Summary table
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"{'Conference':<20} {'Papers':<10} {'Abstract':<15} {'Status':<15}")
    print("-" * 60)
    
    for r in results:
        status_icon = "✅" if r['status'] == "SUCCESS" else "❌"
        abstract_str = f"{r['abstract']} chars" if isinstance(r['abstract'], int) and r['abstract'] > 0 else str(r['abstract'])
        print(f"{status_icon} {r['name']:<18} {r['papers']:<10} {abstract_str:<15} {r['status']:<15}")
    
    success_count = sum(1 for r in results if r['status'] == "SUCCESS")
    print(f"\n✨ Total: {success_count}/{len(results)} conferences with working abstract extraction")


if __name__ == "__main__":
    test_all_conferences()
