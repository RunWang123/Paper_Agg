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
from scanner import Scanner
# Import embedding functions
from embeddings import create_paper_embedding_text, generate_embedding

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("arxiv_backfill")

ARXIV_API_URL = "http://export.arxiv.org/api/query"
RATE_LIMIT_DELAY = 3.0  # Seconds between requests

def clean_title_for_search(title):
    # Remove special characters for search query
    cleaned = re.sub(r'[^a-zA-Z0-9]', ' ', title)
    return re.sub(r'\s+', ' ', cleaned).strip()

def normalize_title(title):
    return re.sub(r'[^a-z0-9]', '', title.lower())

def search_arxiv(title):
    cleaned_query = clean_title_for_search(title)
    query_param = f'ti:"{cleaned_query}"'
    encoded_query = urllib.parse.quote(query_param)
    
    url = f"{ARXIV_API_URL}?search_query={encoded_query}&start=0&max_results=1"
    
    try:
        with urllib.request.urlopen(url) as response:
            xml_data = response.read()
            
        root = ET.fromstring(xml_data)
        ns = {'atom': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}
        
        entry = root.find('atom:entry', ns)
        if entry is not None:
            arxiv_title = entry.find('atom:title', ns).text.strip()
            summary = entry.find('atom:summary', ns).text.strip()
            link = entry.find('atom:id', ns).text.strip()
            
            # Extract authors
            authors = []
            for author in entry.findall('atom:author', ns):
                name = author.find('atom:name', ns).text.strip()
                authors.append(name)
            authors_str = ", ".join(authors)
            
            # Verify match
            norm_db_title = normalize_title(title)
            norm_arxiv_title = normalize_title(arxiv_title)
            
            if norm_db_title == norm_arxiv_title:
                return {
                    "abstract": summary,
                    "arxiv_url": link,
                    "title": arxiv_title,
                    "authors": authors_str
                }
            else:
                logger.info(f"Mismatch: DB='{title}' vs ArXiv='{arxiv_title}'")
                return None
                
    except Exception as e:
        logger.error(f"ArXiv request failed: {e}")
        return None
    
    return None

def run_backfill(limit=0, dry_run=False):
    init_db()
    session = SessionLocal()
    
    # metrics
    count_updated = 0
    count_embeddings = 0
    
    # 1. Backfill Abstracts & Authors
    papers = session.query(Paper).filter(
        Paper.conference == "CVPR", 
        Paper.year == 2025,
        (Paper.abstract == None) | (Paper.abstract == "")
    ).all()
    
    logger.info(f"Found {len(papers)} CVPR 2025 papers missing abstracts.")
    
    if limit > 0:
        logger.info(f"Limiting processing to first {limit} papers.")
        papers = papers[:limit]
    
    for i, paper in enumerate(papers):
        logger.info(f"[{i+1}/{len(papers)}] Searching ArXiv for: {paper.title[:50]}...")
        
        result = search_arxiv(paper.title)
        
        if result:
            logger.info("  ✅ Found on ArXiv!")
            logger.info(f"     Title: {result['title']}")
            logger.info(f"     Authors: {result['authors']}")
            logger.info(f"     Abstract Length: {len(result['abstract'])}")
            
            if dry_run:
                logger.info("     [DRY RUN] Would update DB and regenerate embedding.")
                time.sleep(1) # simulate
                continue

            paper.abstract = result['abstract']
            
            # Update authors if new list is longer/better (heuristic)
            if result['authors'] and len(result['authors']) > len(paper.authors or ""):
                 paper.authors = result['authors']
            
            if not paper.tags: paper.tags = []
            if "arxiv" not in paper.tags: paper.tags.append("arxiv")
            
            # Regenerate embedding immediately with new data
            try:
                text_for_embedding = create_paper_embedding_text(
                    title=paper.title,
                    authors=paper.authors or "",
                    abstract=paper.abstract or ""
                )
                embedding = generate_embedding(text_for_embedding)
                
                # We need to execute raw SQL for pgvector update usually, 
                # but let's try assuming the ORM might handle it if mapped, 
                # otherwise use raw SQL like scanner.py
                update_sql = text("UPDATE papers SET embedding = :embedding WHERE id = :id")
                session.execute(update_sql, {"embedding": str(embedding), "id": paper.id})
                count_embeddings += 1
            except Exception as e:
                 logger.error(f"  ❌ Embedding failed: {e}")

            session.commit() # Commit this paper's updates
            count_updated += 1
        else:
            logger.info("  ❌ Not found.")
            
        time.sleep(RATE_LIMIT_DELAY)

    logger.info(f"Backfill complete.")
    if dry_run:
        logger.info("  [DRY RUN] No changes were made to the database.")
    else:
        logger.info(f"  - Abstracts updated: {count_updated}")
        logger.info(f"  - Embeddings regenerated: {count_embeddings}")
    session.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Backfill missing abstracts from ArXiv")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of papers to process (0 for all)")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without saving to DB")
    args = parser.parse_args()
    
    run_backfill(limit=args.limit, dry_run=args.dry_run)
