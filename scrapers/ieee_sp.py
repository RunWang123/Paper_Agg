from .base import EventScraper, PaperData
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class IEEESPScraper(EventScraper):
    def scrape(self, url: str) -> list[PaperData]:
        papers = []
        soup = self.get_soup(url)
        if not soup:
            return papers

        # IEEE S&P via DBLP (dblp.org/db/conf/sp/spYYYY.html)
        # DBLP Layout (same as ACM CCS and USENIX):
        # <li class="entry inproceedings" ...>
        #   <cite class="data" ...>
        #     <span class="title" itemprop="name">Paper Title.</span>
        #     <span itemprop="author" ...><a ...><span itemprop="name">Author Name</span></a></span>
        #     ...
        #   </cite>
        # </li>
        
        items = soup.find_all('li', class_='entry inproceedings')
        
        for li in items:
            cite = li.find('cite', class_='data')
            if not cite: continue
            
            # Title
            title_span = cite.find('span', class_='title', itemprop='name')
            if not title_span: continue
            title = title_span.get_text(strip=True)
            
            # Authors
            author_spans = cite.find_all('span', itemprop='author')
            authors_list = []
            for author_span in author_spans:
                name_span = author_span.find('span', itemprop='name')
                if name_span:
                    authors_list.append(name_span.get_text(strip=True))
            
            authors = ", ".join(authors_list)
            
            # Link - usually to DOI or IEEE
            # The link is usually in <nav class="publ"> with <ul> <li> <a href="...">
            nav = li.find('nav', class_='publ')
            link = url
            if nav:
                # Find link with 'electronic edition' or just first link
                ul = nav.find('ul')
                if ul:
                    first_a = ul.find('a')
                    if first_a:
                         link = first_a.get('href')
            
            papers.append(PaperData(
                title=title,
                authors=authors,
                url=link,
                pdf_url=None
            ))
            
        return papers
