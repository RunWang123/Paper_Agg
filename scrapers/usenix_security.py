from .base import EventScraper, PaperData
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class USENIXScraper(EventScraper):
    def scrape(self, url: str) -> list[PaperData]:
        papers = []
        soup = self.get_soup(url)
        if not soup:
            return papers

        # USENIX Security via DBLP (dblp.org/db/conf/uss/ussYYYY.html)
        # DBLP Layout (same as ACM CCS):
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
            
            # Link - usually to USENIX open access or DOI
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

    def scrape_abstract(self, paper_url: str) -> str:
        """
        Scrape abstract from USENIX paper page.
        USENIX paper pages have the abstract in div.field-name-field-paper-description
        """
        if not paper_url or 'usenix.org' not in paper_url:
            return ""
        
        soup = self.get_soup(paper_url)
        if not soup:
            return ""
        
        # USENIX uses this specific class for paper description/abstract
        abstract_div = soup.find('div', class_='field-name-field-paper-description')
        if abstract_div:
            text = abstract_div.get_text(strip=True)
            if len(text) > 50:
                return text
        
        # Fallback: try meta description
        meta = soup.find('meta', {'name': 'description'})
        if meta:
            content = meta.get('content', '')
            if len(content) > 100:
                return content
        
        return ""
