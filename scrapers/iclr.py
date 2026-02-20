from .base import EventScraper, PaperData
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests
import json

class ICLRScraper(EventScraper):
    def scrape(self, url: str) -> list[PaperData]:
        # Try JSON first for rich data (2023, 2024)
        papers = self.scrape_from_json(self.year)
        if papers:
            print(f"  [ICLR] Found {len(papers)} papers via JSON source.")
            return papers
            
        print("  [ICLR] JSON source not found/empty. Falling back to HTML scraping.")
        return self.scrape_from_html(url)

    def scrape_from_json(self, year: int) -> list[PaperData]:
        """
        Tries to fetch papers from the hidden JSON data source used by the virtual site.
        Url: https://iclr.cc/static/virtual/data/iclr-{year}-orals-posters.json
        """
        json_url = f"https://iclr.cc/static/virtual/data/iclr-{year}-orals-posters.json"
        
        try:
            # Use same headers/setup as base scraper
            # We can't use self.get_soup here easily, just use requests
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            }
            response = requests.get(json_url, headers=headers, timeout=30, verify=False)
            
            if response.status_code != 200:
                return []
                
            data = response.json()
            results = data.get('results', [])
            if not results:
                return []
                
            papers_map = {} # Dedup by ID or title
            
            for item in results:
                # 1. Title
                title = item.get('name', '').strip()
                if not title: continue
                
                # 2. Authors
                author_list = item.get('authors', [])
                if isinstance(author_list, list):
                    authors = ", ".join([a.get('fullname', '') for a in author_list if 'fullname' in a])
                else:
                    authors = str(author_list)
                    
                # 3. URLs
                # 'id' is often the openreview ID or internal ID
                # item['url'] is usually internal like "poster_123.html"
                # item['paper_pdf_url'] is usually empty, check paper_url (OpenReview)
                pdf_url = item.get('paper_pdf_url')
                
                if not pdf_url:
                    # Generic function to extract ID from OpenReview URL
                    def extract_pdf_from_or_url(u):
                        if u and 'openreview.net/forum' in u and 'id=' in u:
                            try:
                                fid = u.split('id=')[1].split('&')[0]
                                return f"https://openreview.net/pdf?id={fid}"
                            except:
                                pass
                        return None

                    # Check paper_url
                    pdf_url = extract_pdf_from_or_url(item.get('paper_url', ''))
                    
                    # Check eventmedia if still missing
                    if not pdf_url:
                        media = item.get('eventmedia', [])
                        for m in media:
                            uri = m.get('uri', '')
                            # Sometimes name="OpenReview"
                            if 'openreview.net/forum' in uri:
                                pdf_url = extract_pdf_from_or_url(uri)
                                if pdf_url: break

                
                # Construct main URL (detail page)
                # Usually /virtual/{year}/poster/{id}
                paper_id = item.get('id')
                paper_url = f"https://iclr.cc/virtual/{year}/poster/{paper_id}"
                
                # 4. Abstract
                abstract = item.get('abstract')
                
                # 5. Tags / Track inference
                tags = []
                
                # "event_type" (2024)
                event_type = item.get('event_type', '')
                if event_type:
                    if 'oral' in event_type.lower(): tags.append("Oral")
                    if 'spotlight' in event_type.lower(): tags.append("Spotlight")
                
                # "decision" / "session" (2023 fallback)
                decision = item.get('decision', '').lower() if item.get('decision') else ''
                session = str(item.get('session', '') if item.get('session') else '').lower()
                
                if 'oral' in decision or 'oral' in session:
                    if "Oral" not in tags: tags.append("Oral")
                
                if 'spotlight' in decision or 'spotlight' in session:
                    if "Spotlight" not in tags: tags.append("Spotlight")
                    
                if 'notable' in decision:
                    if "Notable" not in tags: tags.append("Notable")
                    # Notable-top-5% is basically Oral/Spotlight equivalent in 2023
                    if 'top-5%' in decision and "Oral" not in tags: tags.append("Oral")
                    if 'top-25%' in decision and "Spotlight" not in tags: tags.append("Spotlight")

                # Combine existing tags
                tag_str = ", ".join(tags) if tags else None
                
                # Deduplication logic
                # Sometimes same paper is in "Poster" AND "Oral" session list in JSON
                # We want to keep the one with better tags or merge them
                if paper_id in papers_map:
                    existing = papers_map[paper_id]
                    # Merge tags
                    new_tags = set(existing.tags.split(", ") if existing.tags else [])
                    if tags: new_tags.update(tags)
                    if new_tags:
                        existing.tags = ", ".join(sorted(list(new_tags)))
                    
                    # Merge PDF (if missing)
                    if not existing.pdf_url and pdf_url:
                        existing.pdf_url = pdf_url
                        
                else:
                    papers_map[paper_id] = PaperData(
                        title=title,
                        authors=authors,
                        url=paper_url,
                        pdf_url=pdf_url,
                        abstract=abstract,
                        tags=tag_str
                    )
            
            return list(papers_map.values())
            
        except Exception as e:
            print(f"  [ICLR] valid JSON fetch failed: {e}")
            return []

    def scrape_from_html(self, url: str) -> list[PaperData]:
        papers = []
        soup = self.get_soup(url)
        if not soup:
            return papers
        
        # Logic for iclr.cc/virtual/YEAR/papers.html
        # Check for list items with links
        lis = soup.find_all('li')
        for li in lis:
            a_tag = li.find('a')
            if not a_tag: continue
            
            href = a_tag.get('href')
            if not href: continue
            
            # Filter for poster links (or oral/spotlight if URL scheme differs, usually /poster/ or /oral/)
            if "/poster/" in href or "/oral/" in href or "/spotlight/" in href:
                title = a_tag.get_text(strip=True)
                
                # Resolve relative link
                if not href.startswith('http'):
                    url_full = urljoin(url, href)
                else:
                    url_full = href
                
                # Authors are missing in the simple HTML list view
                authors = "Visit Detail Page"
                
                papers.append(PaperData(
                    title=title,
                    authors=authors,
                    url=url_full,
                    pdf_url=None
                ))
                
        # Fallback to card logic (older years? or specific views)
        if not papers:
            cards = soup.find_all('div', class_='card')
            for card in cards:
                h3 = card.find('h3', class_='card-title')
                if not h3: continue
                
                a_tag = h3.find('a')
                if not a_tag: continue
                
                title = a_tag.get_text(strip=True)
                link = a_tag['href']
                
                if not link.startswith('http'):
                    link = urljoin(url, link)
                    
                # Authors
                subtitle = card.find('div', class_='card-subtitle')
                authors = subtitle.get_text(strip=True) if subtitle else "Unknown"
                    
                papers.append(PaperData(
                    title=title,
                    authors=authors,
                    url=link,
                    pdf_url=None
                ))
            
        return papers
