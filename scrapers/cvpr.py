from .base import PlaywrightScraper, PaperData
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote
import logging
import time
import re

logger = logging.getLogger(__name__)

class CVPRScraper(PlaywrightScraper):
    def scrape(self, url: str) -> list[PaperData]:
        papers = []
        
        # Check if we need Playwright (for 2025+ or if dynamic)
        use_playwright = "AcceptedPapers" in url
        
        soup = None
        if use_playwright:
            logger.info(f"🎭 Using Playwright for {url} (Dynamic Content)")
            # Wait for specific element to ensure load, e.g. a table cell or strong tag
            soup = self.get_dynamic_soup(url, scroll=True, wait_selector='strong')
        
        if not soup:
            try:
                if not use_playwright:
                     soup = self.get_soup(url)
                elif not soup:
                     pass
            except Exception as e:
                logger.error(f"Failed to fetch {url}: {e}")
                return []

        if not soup:
            return []

        # Logic for openaccess.thecvf.com (Standard CVF Archive - Static)
        if "openaccess.thecvf.com" in url:
            # ... (Old logic for openaccess - kept for compatibility)
            titles = soup.find_all('dt', class_='ptitle')
            for dt in titles:
                link = dt.find('a')
                if link:
                    title = link.get_text(strip=True)
                    relative_link = link.get('href')
                    full_url = urljoin(url, relative_link)
                    
                    dd = dt.find_next_sibling('dd')
                    authors = "Unknown"
                    if dd:
                        form = dd.find('form', class_='auth_search_form')
                        if form:
                            author_links = form.find_all('a')
                            authors = ", ".join([a.get_text(strip=True) for a in author_links])
                        else:
                            authors = dd.get_text(strip=True)
                            
                    pdf_url = None
                    dd2 = dd.find_next_sibling('dd') if dd else None
                    if dd2:
                         pdf_link = dd2.find('a', string='pdf')
                         if pdf_link:
                             pdf_url = urljoin(url, pdf_link.get('href'))
                         else:
                             for l in dd2.find_all('a'):
                                 if 'pdf' in l.get_text(strip=True).lower() or l.get('href', '').endswith('.pdf'):
                                     pdf_url = urljoin(url, l.get('href'))
                                     break

                    papers.append(PaperData(
                        title=title,
                        authors=authors,
                        url=full_url,
                        pdf_url=pdf_url
                    ))
            return papers

        # Logic for Dynamic CVPR 2025 "Accepted Papers" page
        if "AcceptedPapers" in url:
             logger.info("  Parsing rendered HTML for CVPR 2025 (Table Mode)...")
             
             # The new logic: Look for Table Rows <tr> match established structure
             # <td> ... <strong>Title</strong> ... Poster Session ... <i>Authors</i> ... </td>
             
             rows = soup.find_all('tr')
             logger.info(f"  Found {len(rows)} table rows.")
             
             for row in rows:
                 title = None
                 full_url = None
                 strong = row.find('strong')
                 
                 # Pattern A: Title in <strong>
                 if strong:
                     title = strong.get_text(strip=True)
                     # Check if strong has a link
                     a_tag = strong.find('a')
                     if a_tag:
                         href = a_tag.get('href')
                         if href:
                             full_url = urljoin(url, href)
                 
                 # Pattern B: Title in <a> (no strong)
                 if not title:
                     # Find first link that looks like a title
                     links = row.find_all('a')
                     for l in links:
                         txt = l.get_text(strip=True)
                         # Heuristics for title link: long enough, not PDF/ProjectPage
                         if len(txt) > 20 and "pdf" not in txt.lower():
                             title = txt
                             href = l.get('href')
                             if href:
                                 full_url = urljoin(url, href)
                             break
                 
                 if not title:
                     # Log skipped row content for debugging (limit to 20)
                     if getattr(self, '_skipped_logged', 0) < 20:
                         logger.info(f"Skipped row (no strong/link): {row.get_text(strip=True)[:100]}")
                         self._skipped_logged = getattr(self, '_skipped_logged', 0) + 1
                     continue

                 # Filtering
                 if len(title) < 5: 
                     logger.info(f"Skipped small title: {title}")
                     continue
                 
                 # Relaxed stop words - only filter very specific non-paper items if they appear in strong tags
                 # Based on debug, most strong tags in rows are papers.
                 # stop_words = ["submit", "registration", "committee", "workshop", "tutorial", "sponsors", "contact", "program", "schedule", "main navigation", "cvpr 2025 accepted papers", "accessibility", "privacy policy", "back to top", "call for", "expo", "careers", "poster session", "all days", "oral session", "award session", "demo session", "doctoral consortium"]
                 
                 # Use regex for whole word matching to avoid false positives (e.g. "program" in "programmatic", "expo" in "exposure")
                 # title_lower = title.lower()
                 # if any(re.search(rf'\b{re.escape(w)}\b', title_lower) for w in stop_words): 
                 #     logger.info(f"Skipped stop word: {title}")
                 #     continue
                 
                 # Extract Authors from <i> inside .indented
                 authors = "Unknown"
                 indented_div = row.find('div', class_='indented')
                 if indented_div:
                     i_tag = indented_div.find('i')
                     if i_tag:
                         authors = i_tag.get_text(strip=True)
                 
                 # If no URL found, generate a stable one
                 if not full_url:
                     # Use Title Slug as anchor
                     slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
                     full_url = f"{url}#{slug}"
                 
                 papers.append(PaperData(
                     title=title,
                     authors=authors,
                     url=full_url,
                     pdf_url=None # PDF usually not available in this view yet
                 ))
                 
             logger.info(f"  Extracted {len(papers)} papers from rows.")
             return papers

        return papers
