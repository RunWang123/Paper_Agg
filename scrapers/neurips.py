from .base import EventScraper, PaperData
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests

class NeurIPSScraper(EventScraper):
    def scrape(self, url: str) -> list[PaperData]:
        papers = []
        soup = self.get_soup(url)
        if not soup:
            return papers

        # Logic for NeurIPS (papers.nips.cc)
        if "nips.cc" in url or "neurips.cc" in url:
            # Usually /paper_files/paper/<year> or just /paper/<year>
            # List of <li><a href="...">Title</a> <a href="..." class="author">...</a></li>
            # OR <div class="container-fluid"> ...
            
            # Check for the paper list container
            # Usually it's a <ul> matching paper list
            ul = soup.find('ul', class_='paper-list')
            if not ul:
                 # Sometimes it's just raw <ul> in <body> or specific div
                 # Fallback: find all <li> that contain <a title="paper title"> or similar structure
                ul = soup.find('div', class_='col-sm-12') # Often wraps the list
            
            if ul:
                items = ul.find_all('li')
                for li in items:
                    a_title = li.find('a', href=True)
                    if not a_title: 
                        continue
                    
                    # NeurIPS titles are links
                    title = a_title.get_text(strip=True)
                    link = urljoin(url, a_title['href'])
                    
                    # Authors are usually "by Author 1, Author 2" text or <i> tag
                    authors_tag = li.find('i')
                    authors = "Unknown"
                    if authors_tag:
                         authors = authors_tag.get_text(strip=True)
                    
                    papers.append(PaperData(
                        title=title,
                        authors=authors,
                        url=link,
                        pdf_url=link.replace("Hash", "Abstract").replace(".html", ".pdf") # Heuristic, might need check
                    ))
            
            # 2024/2025 might use a different schedule page (neurips.cc/Conferences/2025/Schedule)
            # If so, the structure is vastly different (virtual schedule).
            # We will assume users point to the Proceedings/Papers list if available.
            
        return papers
