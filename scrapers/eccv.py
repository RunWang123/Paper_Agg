from .base import EventScraper, PaperData
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class ECCVScraper(EventScraper):
    def scrape(self, url: str) -> list[PaperData]:
        papers = []
        soup = self.get_soup(url)
        if not soup:
            return papers

        # Logic for ecva.net/papers.php
        # Structure:
        # <div id="content">
        #   <div class="accordion-header">ECCV 2024</div>
        #   <div class="accordion-content">
        #       <dt class="ptitle"><a href="...">Title</a></dt>
        #       <dd>Authors</dd>
        #   </div>
        # </div>
        #
        # Note: The page often contains ALL years. We might need to filter by the requested year header.
        # However, the user config points to the same URL for all years. 
        # Ideally, we find the section for self.year.
        if not soup:
            return papers

        # Determine the logic based on the URL
        # For ecva.net/papers.php
        
        # Heuristic: Find the header "ECCV <Year>" and parse siblings until next header
        
        content_div = soup.find('div', id='content')
        if not content_div:
            content_div = soup.find('div', class_='content')
            
        if not content_div:
             # Fallback to body?
             content_div = soup.body
        
        # Heuristic: Find the header "ECCV <Year>" in the whole soup
        
        target_header = None
        # Headers are usually <h3> or <div class="accordion-header">
        # 2024 uses <button class="accordion">ECCV 2024 Papers</button>
        # Search in soup.find_all because the header might be outside the 'content' div
        candidates = soup.find_all(['h3', 'div', 'button'], class_=['accordion-header', 'accordion', 'ptitle'])
        
        for header in candidates:
            if f"ECCV {self.year}" in header.get_text():
                target_header = header
                break
        
        container = None
        if target_header:
            # The papers are in the 'next sibling' div usually "accordion-content"
            container = target_header.find_next_sibling('div', class_='accordion-content')
        
        if not container:
            # Fallback for old years or if header not found but 'content' div exists and seems right?
            # If we are scraping a specific year url (like 2022 if it was separate, but here it is one page)
            # We must be careful.
            
            # If default content_div logic found something, check if it looks like the right year?
            # Hard to tell.
            pass

        if not container and content_div:
             # Try to use content_div as fallback if we couldn't match header
             # But this risks getting wrong year.
             # However, for now let's use it if we are desperate.
             pass
             
        if not container:
             return papers
        
        dt_list = container.find_all('dt', class_='ptitle')
        for dt in dt_list:
            a_tag = dt.find('a')
            if not a_tag: continue
            
            title = a_tag.get_text(strip=True)
            link = a_tag['href']
            # Resolve relative link
            if not link.startswith('http'):
                 link = urljoin(url, link)
            
            dd = dt.find_next_sibling('dd')
            authors = dd.get_text(strip=True) if dd else "Unknown"
            
            papers.append(PaperData(
                title=title,
                authors=authors,
                url=link,
                pdf_url=link.replace(".php", ".pdf") if "openaccess" in link else None 
                # ECVA links are like papers/eccv_2022/papers_ECCV/html/....php
                # PDFs are often ../papers_ECCV/papers/....pdf
                # We can leave pdf_url None or try to guess.
            ))
            
        return papers
