"""
IEEE VIS Conference Scraper
Scrapes papers from ieeevis.org
"""

from .base import EventScraper, PaperData
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import Optional
import time


class IEEEVISScraper(EventScraper):
    """Scraper for IEEE VIS conference (Visualization)."""
    
    def scrape(self, url: str) -> list[PaperData]:
        """
        Scrape papers from IEEE VIS.
        
        URL format: https://ieeevis.org/year/YYYY/program/event_v-full.html
        This page contains sessions, each session has papers.
        """
        papers = []
        soup = self.get_soup(url)
        if not soup:
            return papers
        
        # Find all session links on the event page
        # Sessions are like: session_full1.html, session_full2.html, etc.
        session_links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if 'session_' in href and href.endswith('.html'):
                full_url = urljoin(url, href)
                if full_url not in session_links:
                    session_links.append(full_url)
        
        print(f"  Found {len(session_links)} sessions")
        
        # Scrape each session for papers
        for session_url in session_links:
            session_papers = self._scrape_session(session_url)
            papers.extend(session_papers)
            time.sleep(0.3)  # Be respectful
        
        return papers
    
    def _scrape_session(self, session_url: str) -> list[PaperData]:
        """Scrape papers from a single session page."""
        papers = []
        soup = self.get_soup(session_url)
        if not soup:
            return papers
        
        # Find all paper links (paper_v-full-XXXX.html or paper_v-tvcg-XXXX.html)
        for a in soup.find_all('a', href=True):
            href = a['href']
            if 'paper_' in href and href.endswith('.html'):
                title = a.get_text(strip=True)
                if not title or len(title) < 10:
                    continue
                
                paper_url = urljoin(session_url, href)
                
                papers.append(PaperData(
                    title=title,
                    authors="See Detail Page",
                    url=paper_url,
                    pdf_url=None
                ))
        
        return papers
    
    def scrape_abstract(self, paper_url: str) -> Optional[str]:
        """
        Extract abstract from IEEE VIS paper page.
        The abstract is in the og:description meta tag.
        """
        soup = self.get_soup(paper_url)
        if not soup:
            return None
        
        # IEEE VIS stores abstract in og:description meta tag
        meta = soup.find('meta', property='og:description')
        if meta and meta.get('content'):
            abstract = meta['content'].strip()
            if len(abstract) > 100:  # Likely an abstract
                return abstract
        
        # Fallback: check name="description"
        meta = soup.find('meta', {'name': 'description'})
        if meta and meta.get('content'):
            abstract = meta['content'].strip()
            if len(abstract) > 100:
                return abstract
        
        # Fallback: look for abstract div
        abstract_div = soup.find('div', class_='abstract')
        if abstract_div:
            return abstract_div.get_text(strip=True)
        
        return None
