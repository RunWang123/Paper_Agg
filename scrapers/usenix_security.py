from .base import EventScraper, PaperData
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class USENIXScraper(EventScraper):
    def scrape(self, url: str) -> list[PaperData]:
        papers = []
        soup = self.get_soup(url)
        if not soup:
            return papers

        # USENIX Technical Sessions page
        # Usually papers are in <article> or <div> with class node-paper
        # e.g. <article class="node node-paper ...">
        
        articles = soup.find_all('article', class_='node-paper')
        
        if not articles:
            # Maybe they are listed in a view?
            # Try finding titles in h2 class node-title
            articles = soup.find_all('h2', class_='node-title')
            # But we need paper container to get authors. 
            # If h2 are used, look at parents?
            if articles:
                 # If we found h2, we iterate them.
                 pass
            else:
                 # fallback to finding links to paper pages
                 pass
        
        # If we found articles using node-paper
        if articles and articles[0].name == 'article':
            for art in articles:
                # In schedule view, it is just <h2><a href>Title</a></h2> without class 'node-title'
                h2 = art.find('h2')
                if not h2: continue
                
                a_tag = h2.find('a')
                if not a_tag: continue
                
                title = a_tag.get_text(strip=True)
                link = urljoin(url, a_tag['href'])
                
                authors_div = art.find('div', class_='field-name-field-paper-people-text')
                if authors_div:
                    authors = authors_div.get_text(strip=True)
                else:
                    authors = "Unknown"
                    
                # PDF is usually in specific span or link
                # <span class="file"><a href="...">PDF</a></span>
                pdf_url = None
                file_span = art.find('span', class_='file')
                if file_span:
                    pdf_a = file_span.find('a')
                    if pdf_a:
                        pdf_url = urljoin(url, pdf_a['href'])
                
                papers.append(PaperData(
                    title=title,
                    authors=authors,
                    url=link,
                    pdf_url=pdf_url
                ))
            return papers
            
        # Fallback for simpler lists or different years
        # USENIX pages are quite consistent (Drupal based). 
        # If the above fails, check if we are on the wrong page type.
        
        return papers
