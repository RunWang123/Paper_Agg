import logging
import time
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("test_arxiv")

# --- duplicated logic from backfill_arxiv.py ---
ARXIV_API_URL = "http://export.arxiv.org/api/query"

def clean_title_for_search(title):
    # Replace non-alphanumeric with space to avoid merging words (e.g. Coarse-to-Fine -> Coarse to Fine)
    cleaned = re.sub(r'[^a-zA-Z0-9]', ' ', title)
    return re.sub(r'\s+', ' ', cleaned).strip()

def normalize_title(title):
    return re.sub(r'[^a-z0-9]', '', title.lower())

def search_arxiv(title):
    logger.info(f"🔎 Searching for: '{title}'")
    cleaned_query = clean_title_for_search(title)
    query_param = f'ti:"{cleaned_query}"'
    encoded_query = urllib.parse.quote(query_param)
    
    url = f"{ARXIV_API_URL}?search_query={encoded_query}&start=0&max_results=1"
    logger.info(f"   API URL: {url}")
    
    try:
        with urllib.request.urlopen(url) as response:
            xml_data = response.read()
            
        root = ET.fromstring(xml_data)
        ns = {'atom': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}
        
        entry = root.find('atom:entry', ns)
        if entry:
            arxiv_title = entry.find('atom:title', ns).text.strip()
            summary = entry.find('atom:summary', ns).text.strip()
            link = entry.find('atom:id', ns).text.strip()
            
            norm_db_title = normalize_title(title)
            norm_arxiv_title = normalize_title(arxiv_title)
            
            logger.info(f"   Found Candidate: '{arxiv_title}'")
            
            if norm_db_title == norm_arxiv_title:
                logger.info("   ✅ MATCH CONFIRMED!")
                return {"abstract": summary, "arxiv_url": link, "title": arxiv_title}
            else:
                logger.info(f"   ❌ Mismatch:\n      Input: {norm_db_title}\n      ArXiv: {norm_arxiv_title}")
                return None
        else:
            logger.info("   ❌ No results found on ArXiv.")
                
    except Exception as e:
        logger.error(f"   ⚠️ Request failed: {e}")
        return None
    
    return None

if __name__ == "__main__":
    print("--- TESTING POSITIVE CASE ---")
    # This paper exists on ArXiv (2503.18872)
    paper_title = "Curriculum Coarse-to-Fine Selection for High-IPC Dataset Distillation"
    result = search_arxiv(paper_title)
    
    if result:
        print("\n✅ SUCCESS: Abstract fetched.")
        print(f"Abstract Preview: {result['abstract'][:100]}...")
    else:
        print("\n❌ FAILURE: Could not find known paper.")

    print("\n\n--- TESTING POSITIVE CASE 2 (Complex Title) ---")
    paper_title_2 = "BiM-VFI: Bidirectional Motion Field-Guided Frame Interpolation for Video with Non-uniform Motions"
    result_2 = search_arxiv(paper_title_2)
    
    if result_2:
        print("\n✅ SUCCESS: Abstract fetched.")
        print(f"Abstract Preview: {result_2['abstract'][:100]}...")
    else:
        print("\n❌ FAILURE: Could not find known paper.")

    print("\n\n--- TESTING NEGATIVE CASE ---")
    fake_title = "This Paper Provide Does Not Exist in ArXiv 2025"
    search_arxiv(fake_title)
    
    print("\n\n--- TESTING MISMATCH CASE ---")
    # Title that exists but we provide slightly wrong
    search_arxiv("Curriculum Coarse-to-Fine Selection for Low-IPC Dataset Distillation") 
