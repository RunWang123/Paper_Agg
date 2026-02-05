import json
import logging
import os
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import SessionLocal, Paper, init_db, IS_POSTGRES
from scrapers.base import EventScraper, PaperData
from scrapers.cvpr import CVPRScraper
from scrapers.iccv import ICCVScraper
from scrapers.eccv import ECCVScraper
from scrapers.ndss import NDSSScraper
from scrapers.neurips import NeurIPSScraper
from scrapers.icml import ICMLScraper
from scrapers.iclr import ICLRScraper
from scrapers.usenix_security import USENIXScraper
from scrapers.ieee_sp import IEEESPScraper
from scrapers.acm_ccs import ACMCCSScraper
from scrapers.ieee_vis import IEEEVISScraper
from sqlalchemy import exists

# Import embedding functions only if PostgreSQL is available
if IS_POSTGRES:
    from embeddings import generate_embedding, create_paper_embedding_text

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Scanner:
    def __init__(self, config_path="config/conferences.json"):
        self.config_path = config_path
        self.scrapers = {}
        self.config = {}
        self.load_config()

    def load_config(self):
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            self.config = {}

    def get_scraper(self, scraper_type, conf_name, year):
        if scraper_type == "CVPR":
            return CVPRScraper(conf_name, year)
        elif scraper_type == "ICCV":
            return ICCVScraper(conf_name, year)
        elif scraper_type == "ECCV":
            return ECCVScraper(conf_name, year)
        elif scraper_type == "NDSS":
            return NDSSScraper(conf_name, year)
        elif scraper_type == "NeurIPS":
            return NeurIPSScraper(conf_name, year)
        elif scraper_type == "ICML":
            return ICMLScraper(conf_name, year)
        elif scraper_type == "ICLR":
            return ICLRScraper(conf_name, year)
        elif scraper_type == "USENIX":
            return USENIXScraper(conf_name, year)
        elif scraper_type == "IEEESP":
            return IEEESPScraper(conf_name, year)
        elif scraper_type == "ACMCCS":
            return ACMCCSScraper(conf_name, year)
        elif scraper_type == "IEEEVIS":
            return IEEEVISScraper(conf_name, year)
        else:
            return None

    def run(self, target_confs=None, fetch_abstracts=True):
        """
        Run configured scrapers and update DB.
        target_confs: Optional list of conference names to scrape (e.g. ['CVPR', 'ICCV']).
                      If None, scrapes all.
        fetch_abstracts: If True (default), fetch abstracts from individual paper pages for semantic search.
                         Set to False for faster scraping without abstracts.
        """
        init_db()
        session = SessionLocal()
        
        # Iterate over the loaded config
        # Structure is { "ConfName": { "scraper": "Type", "years": { "2024": "url" } } }
        logger.info(f"Starting scan with {len(self.config)} conferences configured")
        logger.info(f"Conferences to process: {list(self.config.keys())}")
        if target_confs:
            logger.info(f"Filtering to only: {target_confs}")
        if fetch_abstracts:
            logger.info("Abstract fetching ENABLED - this will be slower")
        
        for conf_name, conf_data in self.config.items():
            # Filter if target_confs is specified
            if target_confs and conf_name not in target_confs:
                logger.debug(f"Skipping {conf_name} (not in target list)")
                continue
            
            logger.info(f"Processing conference: {conf_name}")
            scraper_type = conf_data.get("scraper")
            years_data = conf_data.get("years", {})
            
            for year_str, url in years_data.items():
                year = int(year_str)
                conf_id = f"{conf_name} {year}"
                
                logger.info(f"Starting scrape for {conf_id}...")
                
                scraper = self.get_scraper(scraper_type, conf_name, year)
                if not scraper:
                    logger.warning(f"No scraper found for type {scraper_type}")
                    continue
                
                try:
                    # Use scrape_with_abstracts if requested
                    if fetch_abstracts:
                        found_papers = scraper.scrape_with_abstracts(url)
                    else:
                        found_papers = scraper.scrape(url)
                    logger.info(f"Found {len(found_papers)} papers for {conf_id}")
                    
                    new_count = 0
                    for p_data in found_papers:
                        if self._save_paper(session, p_data, conf_name, year, url):
                            new_count += 1
                    
                    session.commit()
                    logger.info(f"Added {new_count} new papers for {conf_id}.")
                    
                    # Add a small delay between scraping different years to be respectful
                    import time
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Failed to scrape {conf_id}: {e}")
                    session.rollback()
        
        session.close()

    def _save_paper(self, session: Session, p_data: PaperData, conf_name: str, year: int, source_url: str) -> bool:
        """
        Save paper to DB if not exists. Returns True if new.
        Auto-generates embedding if PostgreSQL with pgvector is available.
        """
        # Check duplicates based on Title + Conference Name + Year
        exists = session.query(Paper).filter(
            Paper.title == p_data.title,
            Paper.conference == conf_name,
            Paper.year == year
        ).first()
        
        if exists:
            return False
        
        new_paper = Paper(
            title=p_data.title,
            authors=p_data.authors,
            conference=conf_name,
            year=year,
            url=p_data.url,
            pdf_url=p_data.pdf_url,
            source_url=source_url,
            tags=p_data.tags,
            abstract=p_data.abstract  # Store abstract for semantic search
        )
        session.add(new_paper)
        session.flush()  # Get the paper ID
        
        # Generate and store embedding if PostgreSQL is available
        if IS_POSTGRES:
            try:
                text_for_embedding = create_paper_embedding_text(
                    title=p_data.title,
                    authors=p_data.authors or "",
                    abstract=p_data.abstract or ""
                )
                embedding = generate_embedding(text_for_embedding)
                update_sql = text(
                    "UPDATE papers SET embedding = :embedding WHERE id = :id"
                )
                session.execute(update_sql, {"embedding": str(embedding), "id": new_paper.id})
            except Exception as e:
                logger.warning(f"Failed to generate embedding for paper {new_paper.id}: {e}")
        
        return True

if __name__ == "__main__":
    scanner = Scanner()
    scanner.run()
