import logging
import time
import sys
import os
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from sqlalchemy import text
import re

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, Paper, init_db
from scanner import Scanner # For _save_paper logic re-use if needed, though we will just update

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("arxiv_backfill")

ARXIV_API_URL = "http://export.arxiv.org/api/query"
RATE_LIMIT_DELAY = 3.0  # Seconds between requests

def clean_title_for_search(title):
    # Remove special characters for search query
    # ArXiv search is sensitive. Replace non-alphanumeric with space.
    cleaned = re.sub(r'[^a-zA-Z0-9]', ' ', title)
    return re.sub(r'\s+', ' ', cleaned).strip()

def normalize_title(title):
    return re.sub(r'[^a-z0-9]', '', title.lower())

def search_arxiv(title):
    cleaned_query = clean_title_for_search(title)
    # Search by title (ti:)
    query_param = f'ti:"{cleaned_query}"'
    encoded_query = urllib.parse.quote(query_param)
    
    url = f"{ARXIV_API_URL}?search_query={encoded_query}&start=0&max_results=1"
    
    try:
        with urllib.request.urlopen(url) as response:
            xml_data = response.read()
            
        root = ET.fromstring(xml_data)
        # Namespace map
        ns = {'atom': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}
        
        entry = root.find('atom:entry', ns)
        if entry is not None:
            arxiv_title = entry.find('atom:title', ns).text.strip()
            summary = entry.find('atom:summary', ns).text.strip()
            link = entry.find('atom:id', ns).text.strip()
            
            # Verify match (ArXiv search is fuzzy, we need to be sure)
            norm_db_title = normalize_title(title)
            norm_arxiv_title = normalize_title(arxiv_title)
            
            # Check for high similarity (exact match of alphanumeric chars)
            if norm_db_title == norm_arxiv_title:
                return {
                    "abstract": summary,
                    "arxiv_url": link,
                    "title": arxiv_title
                }
            else:
                logger.info(f"Mismatch: DB='{title}' vs ArXiv='{arxiv_title}'")
                return None
                
    except Exception as e:
        logger.error(f"ArXiv request failed: {e}")
        return None
    
    return None

def run_backfill():
    init_db()
    session = SessionLocal()
    
    # Find papers with NO abstract
    # Limit to CVPR 2025 for now (focus area)
    papers = session.query(Paper).filter(
        Paper.conference == "CVPR", 
        Paper.year == 2025,
        (Paper.abstract == None) | (Paper.abstract == "")
    ).all()
    
    logger.info(f"Found {len(papers)} CVPR 2025 papers missing abstracts.")
    
    count_updated = 0
    
    for i, paper in enumerate(papers):
        logger.info(f"[{i+1}/{len(papers)}] Searching ArXiv for: {paper.title[:50]}...")
        
        result = search_arxiv(paper.title)
        
        if result:
            logger.info("  ✅ Found on ArXiv!")
            paper.abstract = result['abstract']
            # Optionally add arxiv link to tags or source_url if we want
            # paper.pdf_url = result['arxiv_url'] # Be careful overwriting
            
            if not paper.tags:
                paper.tags = []
            if "arxiv" not in paper.tags:
                paper.tags.append("arxiv")
                
            session.commit()
            count_updated += 1
        else:
            logger.info("  ❌ Not found or mismatch.")
            
        # Respect Rate Limit
        time.sleep(RATE_LIMIT_DELAY)
        
    logger.info(f"Backfill complete. Updated {count_updated} papers.")
    session.close()

if __name__ == "__main__":
    run_backfill()
