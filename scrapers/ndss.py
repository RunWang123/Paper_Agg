from .base import EventScraper, PaperData
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class NDSSScraper(EventScraper):
    def scrape(self, url: str) -> list[PaperData]:
        papers = []
        soup = self.get_soup(url)
        if not soup:
            return papers

        # NDSS via DBLP (dblp.org/db/conf/ndss/ndssYYYY.html)
        # DBLP Layout (same as ACM CCS, USENIX, and IEEE S&P):
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
            
            # Link - usually to NDSS proceedings or DOI
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
        Scrape abstract from NDSS paper page.
        NDSS paper pages at ndss-symposium.org have the abstract in the article body.
        """
        if not paper_url or 'ndss-symposium.org' not in paper_url:
            return ""
        
        soup = self.get_soup(paper_url)
        if not soup:
            return ""
        
        # Find the article or main content div
        article = soup.find('article') or soup.find('div', class_='paper-data')
        if article:
            paragraphs = article.find_all('p')
            # Usually the abstract is the third paragraph (after author info)
            for p in paragraphs:
                text = p.get_text(strip=True)
                # Skip short paragraphs or author info
                if len(text) > 200 and 'university' not in text.lower()[:100]:
                    return text
        
        # Fallback: try meta description
        meta = soup.find('meta', {'name': 'description'})
        if meta:
            content = meta.get('content', '')
            if len(content) > 100:
                return content
        
        return ""
