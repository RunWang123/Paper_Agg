from .base import EventScraper, PaperData
import re

class NDSSScraper(EventScraper):
    def scrape(self, url: str) -> list[PaperData]:
        soup = self.get_soup(url)
        papers = []
        if not soup:
            return papers

        # Logic based on 2025 NDSS Accepted Papers page structure:
        # <div class="tag-box rel-paper">
        #   <div class="selected-post-text-area rel-paper-in">
        #      <h3 class="blog-post-title">Title...</h3>
        #      <p>Authors...</p>
        #      <a class="paper-link-abs" href="...">More Details</a>
        #   </div>
        # </div>

        paper_blocks = soup.find_all('div', class_='rel-paper')
        
        for block in paper_blocks:
            # Title
            h3 = block.find('h3', class_='blog-post-title')
            if not h3:
                continue
            
            title = h3.get_text(strip=True)
            
            # Authors are in the <p> tag sibling/child
            # The structure shows h3 and p as siblings inside selected-post-text-area
            p_author = block.find('p')
            authors = "Unknown"
            if p_author:
                authors = p_author.get_text(strip=True)

            # Link
            a_link = block.find('a', class_='paper-link-abs')
            link = url
            if a_link:
                link = a_link.get('href')

            papers.append(PaperData(
                title=title,
                authors=authors,
                url=link,
                pdf_url=None # PDF usually on the details page, skip for now or can fetch if needed
            ))
            
        return papers
