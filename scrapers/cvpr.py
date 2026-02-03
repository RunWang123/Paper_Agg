from .base import EventScraper, PaperData
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class CVPRScraper(EventScraper):
    def scrape(self, url: str) -> list[PaperData]:
        soup = self.get_soup(url)
        papers = []
        if not soup:
            return papers

        # Logic for openaccess.thecvf.com (Standard CVF Archive)
        if "openaccess.thecvf.com" in url:
            # Usually <dt class="ptitle"><a href="...">Title</a></dt>
            # <dd class="baseys">Authors</dd>
            
            # Find all independent paper blocks
            # They are usually in <div id="content"> <dl>
            dt_list = soup.find_all('dt', class_='ptitle')
            for dt in dt_list:
                a_tag = dt.find('a')
                if not a_tag:
                    continue
                
                title = a_tag.get_text(strip=True)
                link = a_tag['href']
                if not link.startswith('http'):
                    # Handle relative links
                    # url base is http://openaccess.thecvf.com
                    base = "http://openaccess.thecvf.com"
                    if link.startswith('/'):
                        link = base + link
                    else: # relative to current path? usually absolute path from root in these sites
                        link = base + '/' + link
                
                # Authors are in the next sibling <dd>
                authors = "Unknown"
                dd = dt.find_next_sibling('dd')
                if dd:
                    # The authors might be in form tag? No, usually text or anchors
                    # <form ...> ... <a href="#">Author</a> ... </form>
                    # Or just text.
                    # Let's get all text
                    authors = dd.get_text(strip=True)
                    # Clean up "Search for keys" helper text if present? 
                    # Usually CVF text clean.
                
                papers.append(PaperData(
                    title=title,
                    authors=authors,
                    url=link,
                    pdf_url=link.replace("html", "pdf") if "html" in link else None
                ))
            return papers

        # Logic for cvpr.thecvf.com or other conference main sites
        # Based on user check, these might be simple lists of links "Title -> Project Page"
        # <ul><li><a href="...">Title</a></li></ul> or similar.
        else:
            # Fallback: Find all links that look like paper titles (long text)
            # This is heuristics based.
            
            # Get main content area to avoid nav links
            main = soup.find('main') or soup.find('div', class_='content') or soup.find('body')
            
            links = main.find_all('a')
            for a in links:
                title = a.get_text(strip=True)
                href = a.get('href')
                
                if not href or not title:
                    continue
                
                # Resolve relative URL
                full_url = urljoin(url, href)
                
                # Heuristics for "Is this a paper?"
                # 1. Length > 20 chars
                # 2. Not a navigation link (Home, Contact, etc.)
                # 3. Not valid for things like "Read More"
                
                if len(title) < 20: 
                    continue
                
                # Check for common non-paper words
                stop_words = ["submit", "registration", "committee", "workshop", "tutorial", "sponsors", "contact", "program", "schedule"]
                if any(w in title.lower() for w in stop_words):
                    continue
                
                # If the URL is external (github, project page), it's likely a paper listed on the conf site
                # Authors might not be present.
                
                papers.append(PaperData(
                    title=title,
                    authors="See Project Page", # Placeholder as authors aren't visible in simple link lists
                    url=full_url,
                    pdf_url=None
                ))

        return papers
