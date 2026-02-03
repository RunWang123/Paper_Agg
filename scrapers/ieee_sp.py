from .base import EventScraper, PaperData
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class IEEESPScraper(EventScraper):
    def scrape(self, url: str) -> list[PaperData]:
        papers = []
        soup = self.get_soup(url)
        if not soup:
            return papers

        # IEEE S&P (ieee-security.org)
        # Program papers page usually has a list.
        # Structure varies by year but often:
        # <ul> <li> <b>Title</b> <br> Authors </li> ... </ul>
        # OR 
        # <div class="paper"> ... </div>
        
        # 2024/2025 might use a table or div structure.
        
        # Try finding bold elements which might be titles?
        # Or search for specific classes.
        
        # Strategy: Look for "modal" or "paper-title" classes if modern site.
        # Older sites (simple HTML): List items.
        
        # Let's try a heuristic: text blocks with significant length separated by known elements.
        
        # Inspecting 2024 site structure (hypothetically):
        # <div class="panel-body"> <p> <b>Title</b> <br> <i>Authors</i> ... </p> </div>
        
        # Strategy: Look for div.list-group-item which contains bold title and collapsible authors
        # This matches sp2024/2025 structure
        
        items = soup.find_all('div', class_='list-group-item')
        if items:
            for item in items:
                # Title is in <b><a>...</a></b>
                b_tag = item.find('b')
                if not b_tag: continue
                
                a_tag = b_tag.find('a')
                if not a_tag:
                    # Sometimes just <b>Title</b>
                    title = b_tag.get_text(strip=True)
                    link = url
                else:
                    title = a_tag.get_text(strip=True)
                    link = a_tag.get('href')
                    if link and not link.startswith('http') and not link.startswith('#'):
                        link = urljoin(url, link)
                    else:
                        link = url # Collapsible link is just anchor

                # Authors in div class="collapse authorlist"
                author_div = item.find('div', class_='authorlist')
                if author_div:
                     # Authors often have superscripts for affiliation, remove them?
                     # text is usually "Name1, Name2..."
                     # get_text might include 1, 2 etc.
                     authors = author_div.get_text(" ", strip=True) 
                else:
                     # Fallback to text parsing if no authorlist div
                     # Item text: Title Authors
                     text = item.get_text(" ", strip=True)
                     authors = text.replace(title, "").strip()

                if len(title) > 5:
                    papers.append(PaperData(
                        title=title,
                        authors=authors,
                        url=link,
                        pdf_url=None
                    ))
            return papers

        # Fallback for older years (simple lists)
        # ... existing fallback logic or new logic for 2022/2023 if they differ ...
        # Based on curl, 2022/2023 might use similar or simple <ul>
        # Let's check if there are <li> elements with bold titles
        
        lis = soup.find_all('li')
        for li in lis:
             # Basic check for title in bold
             b_tag = li.find(['b', 'strong'])
             if b_tag:
                 title = b_tag.get_text(strip=True)
                 if len(title) < 10: continue
                 
                 text = li.get_text(" ", strip=True)
                 authors = text.replace(title, "").strip().lstrip(".,- ")
                 
                 papers.append(PaperData(
                    title=title, 
                    authors=authors,
                    url=url,
                    pdf_url=None
                 ))
                 
        return papers
