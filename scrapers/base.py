from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
import time

@dataclass
class PaperData:
    title: str
    authors: str
    url: str
    pdf_url: Optional[str] = None
    tags: Optional[str] = None  # Comma-separated tags
    abstract: Optional[str] = None  # Paper abstract for semantic search


class EventScraper(ABC):
    def __init__(self, conference_name: str, year: int):
        self.conference_name = conference_name
        self.year = year

    @abstractmethod
    def scrape(self, url: str) -> List[PaperData]:
        pass

    def scrape_with_abstracts(self, url: str, delay: float = 0.5) -> List[PaperData]:
        """
        Scrape papers and fetch abstracts from individual paper pages.
        This is slower but provides better data for semantic search.
        """
        papers = self.scrape(url)
        
        for i, paper in enumerate(papers):
            if paper.abstract:  # Skip if already has abstract
                continue
            
            try:
                abstract = self.scrape_abstract(paper.url)
                if abstract:
                    paper.abstract = abstract
                    
                # Progress logging
                if (i + 1) % 10 == 0:
                    print(f"  Fetched abstracts: {i + 1}/{len(papers)}")
                    
                # Be respectful to servers
                time.sleep(delay)
            except Exception as e:
                print(f"  Failed to get abstract for {paper.title[:50]}: {e}")
                
        return papers

    def scrape_abstract(self, paper_url: str) -> Optional[str]:
        """
        Fetch abstract from a paper's detail page.
        Override this in subclasses for conference-specific extraction.
        """
        soup = self.get_soup(paper_url)
        if not soup:
            return None
        
        # Common abstract extraction patterns
        abstract = None
        
        # Pattern 1: CVF/ECVA style - div#abstract
        div = soup.find('div', id='abstract')
        if div:
            abstract = div.get_text(strip=True)
            if abstract:
                return abstract
        
        # Pattern 2: Meta tag
        meta = soup.find('meta', {'name': 'description'})
        if meta and meta.get('content'):
            content = meta['content'].strip()
            if len(content) > 100:  # Likely an abstract, not just a tagline
                return content
        
        # Pattern 3: Element with class containing 'abstract'
        for div in soup.find_all(['div', 'p', 'section'], class_=lambda x: x and 'abstract' in x.lower() if x else False):
            text = div.get_text(strip=True)
            if text and len(text) > 100:
                return text
        
        # Pattern 4: NeurIPS/ICLR/OpenReview - div.card-text or similar
        for div in soup.find_all('div', class_=['card-text', 'abstract-text', 'note-content']):
            text = div.get_text(strip=True)
            if text and len(text) > 100:
                return text
        
        # Pattern 5: Look for heading "Abstract" followed by text
        for heading in soup.find_all(['h2', 'h3', 'h4', 'strong']):
            if 'abstract' in heading.get_text().lower():
                next_elem = heading.find_next_sibling(['p', 'div'])
                if next_elem:
                    text = next_elem.get_text(strip=True)
                    if text and len(text) > 50:
                        return text
        
        return None

    def get_soup(self, url: str):
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                # Use comprehensive browser headers to avoid bot detection
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Cache-Control': 'max-age=0',
                }
                
                # Add a small delay between requests to be respectful
                if attempt > 0:
                    time.sleep(retry_delay * attempt)
                
                response = requests.get(url, headers=headers, timeout=30, verify=False)
                response.raise_for_status()
                return BeautifulSoup(response.content, 'html.parser')
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 403 and attempt < max_retries - 1:
                    print(f"Got 403 error for {url}, retrying in {retry_delay * (attempt + 1)}s...")
                    continue
                print(f"Error fetching {url}: {e}")
                return None
            except Exception as e:
                print(f"Error fetching {url}: {e}")
                return None
        
        return None
