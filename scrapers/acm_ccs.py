from .base import EventScraper, PaperData
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class ACMCCSScraper(EventScraper):
    def scrape(self, url: str) -> list[PaperData]:
        papers = []
        soup = self.get_soup(url)
        if not soup:
            return papers

        # ACM CCS via DBLP (config points to dblp.org/db/conf/ccs/ccsYYYY.html)
        # DBLP Layout:
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
            
            # Link - usually to DOI
            # outer li has lists of links usually in <nav class="publ">
            # But inside cite, there might be no link to paper directly?
            # DBLP usually has links in the 'ee' (electronic edition) icon list next to the entry
            # But the 'title' often is not a link in DBLP.
            # The link is usually in <ul class="publ-list"> <li> <div class="head"> <a href="...">
            # Wait, the 'li' is the entry.
            # Inside 'li', there is <nav class="publ"> with <ul> <li> <a href="DOI URL">
            
            nav = li.find('nav', class_='publ')
            link = url
            if nav:
                # Find link with 'electronic edition' or just first link
                ul = nav.find('ul')
                if ul:
                    first_a = ul.find('a')
                    if first_a:
                         link = first_a.get('href')
            
            # Tag Short Papers (<= 6 pages)
            tags = None
            pagination = cite.find('span', itemprop='pagination')
            if pagination:
                pages = pagination.get_text(strip=True)
                page_count = 0
                if "-" in pages:
                    try:
                        start, end = pages.split("-")
                        if ":" in start: start = start.split(":")[-1]
                        if ":" in end: end = end.split(":")[-1]
                        page_count = int(end) - int(start) + 1
                    except:
                        pass
                else:
                    page_count = 1
                
                if page_count > 0 and page_count <= 6:
                    tags = "Short Paper"
                         
            papers.append(PaperData(
                title=title,
                authors=authors,
                url=link,
                pdf_url=None,
                tags=tags
            ))
            
        return papers
