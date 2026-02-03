from .base import EventScraper, PaperData
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests

class ICMLScraper(EventScraper):
    def scrape(self, url: str) -> list[PaperData]:
        papers = []
        soup = self.get_soup(url)
        if not soup:
            return papers

        # Logic for icml.cc/virtual/YEAR/papers.html (Same as ICLR)
        
        # Check for list items with poster/oral links
        lis = soup.find_all('li')
        found_li_papers = False
        
        for li in lis:
            a_tag = li.find('a')
            if not a_tag: continue
            
            href = a_tag.get('href')
            if not href: continue
            
            # Filter for poster/oral links
            # ICML might use /poster/, /oral/, /spotlight/
            if "/poster/" in href or "/oral/" in href or "/spotlight/" in href:
                title = a_tag.get_text(strip=True)
                
                if not href.startswith('http'):
                    url_full = urljoin(url, href)
                else:
                    url_full = href
                
                authors = "Visit Detail Page"
                
                papers.append(PaperData(
                    title=title,
                    authors=authors,
                    url=url_full,
                    pdf_url=None
                ))
                found_li_papers = True

        if found_li_papers:
            return papers

        # Fallback to card logic (older years or different view)
        cards = soup.find_all('div', class_='card')
        for card in cards:
            h3 = card.find('h3', class_='card-title')
            if not h3: continue
            
            a_tag = h3.find('a')
            if not a_tag: continue
            
            title = a_tag.get_text(strip=True)
            if not title: continue # skip empty titles
            
            link = a_tag['href']
            if not link.startswith('http'):
                link = urljoin(url, link)
                
            subtitle = card.find('div', class_='card-subtitle')
            authors = subtitle.get_text(strip=True) if subtitle else "Unknown"
            
            papers.append(PaperData(
                title=title,
                authors=authors,
                url=link,
                pdf_url=None
            ))
            
        # Keep legacy PMLR logic as fallback if URL contains mlr.press?
        # Config updated to icml.cc so this branch might not trigger, but good to keep if needed.
        if "mlr.press" in url:
             paper_divs = soup.find_all('div', class_='paper')
             for div in paper_divs:
                title_tag = div.find('p', class_='title')
                if not title_tag: continue
                title = title_tag.get_text(strip=True)
                
                links_para = div.find('p', class_='links')
                pdf_link = None
                abs_link = url
                
                if links_para:
                    for a in links_para.find_all('a'):
                        txt = a.get_text(strip=True).lower()
                        href = a['href']
                        if 'pdf' in txt:
                            pdf_link = href
                        elif 'abs' in txt:
                            abs_link = href
                
                authors_span = div.find('span', class_='authors')
                authors = authors_span.get_text(strip=True) if authors_span else "Unknown"
                
                papers.append(PaperData(
                    title=title,
                    authors=authors,
                    url=abs_link,
                    pdf_url=pdf_link
                ))
        
        return papers
