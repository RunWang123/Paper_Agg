from .base import EventScraper, PaperData
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests

class ICLRScraper(EventScraper):
    def scrape(self, url: str) -> list[PaperData]:
        papers = []
        soup = self.get_soup(url)
        if not soup:
            return papers
        
        # Logic for iclr.cc/virtual/YEAR/papers.html
        # 2024 structure: <ul> <li> <a href="/virtual/2024/poster/ID">Title</a> </li> ... </ul>
        
        # Check for list items with links
        lis = soup.find_all('li')
        for li in lis:
            a_tag = li.find('a')
            if not a_tag: continue
            
            href = a_tag.get('href')
            if not href: continue
            
            # Filter for poster links (or oral/spotlight if URL scheme differs, usually /poster/ or /oral/)
            if "/poster/" in href or "/oral/" in href or "/spotlight/" in href:
                title = a_tag.get_text(strip=True)
                
                # Resolve relative link
                if not href.startswith('http'):
                    url_full = urljoin(url, href)
                else:
                    url_full = href
                
                # Authors are NOT in the list item usually in this view?
                # "Title" is only text.
                # Authors might be missing. PaperData requires authors.
                # We can put "See detail page" or parse more if possible.
                # Sometimes the list is `Title by Authors`? 
                # Based on grep output: <li><a ...>Title</a></li>
                # So authors are missing in this view.
                authors = "Visit Detail Page"
                
                papers.append(PaperData(
                    title=title,
                    authors=authors,
                    url=url_full,
                    pdf_url=None
                ))
                
        # Fallback to card logic (older years?)
        if not papers:
            cards = soup.find_all('div', class_='card')
            for card in cards:
                h3 = card.find('h3', class_='card-title')
                if not h3:
                    # older years might be different
                    continue
                
                a_tag = h3.find('a')
                if not a_tag: continue
                
                title = a_tag.get_text(strip=True)
                link = a_tag['href']
                
                # Resolve relative link
                if not link.startswith('http'):
                    link = urljoin(url, link)
                    
                # Authors
                subtitle = card.find('div', class_='card-subtitle')
                if subtitle:
                    authors = subtitle.get_text(strip=True)
                else:
                    authors = "Unknown"
                    
                papers.append(PaperData(
                    title=title,
                    authors=authors,
                    url=link,
                    pdf_url=None # PDF usually inside the detail page
                ))
            
        return papers
