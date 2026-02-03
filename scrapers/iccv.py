from .base import EventScraper, PaperData
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class ICCVScraper(EventScraper):
    def scrape(self, url: str) -> list[PaperData]:
        soup = self.get_soup(url)
        papers = []
        if not soup:
            return papers

        if "dblp.org" in url:
            # DBLP Scraping (Same as ACM CCS)
            # Layout: <li class="entry inproceedings"> <cite class="data"> <span class="title">...</span> ... </cite> </li>
            items = soup.find_all('li', class_='entry inproceedings')
            for li in items:
                cite = li.find('cite', class_='data')
                if not cite: continue
                
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
                
                # Link
                nav = li.find('nav', class_='publ')
                link = url
                if nav:
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

        elif "openaccess.thecvf.com" in url:
            # Legacy CVF OpenAccess
            # <dt class="ptitle"><a href="...">Title</a></dt>
            # <dd class="baseys">Authors</dd>
            
            dt_list = soup.find_all('dt', class_='ptitle')
            for dt in dt_list:
                a_tag = dt.find('a')
                if not a_tag: continue
                
                title = a_tag.get_text(strip=True)
                link = a_tag['href']
                if not link.startswith('http'):
                    base = "http://openaccess.thecvf.com"
                    if link.startswith('/'):
                        link = base + link
                    else:
                        link = base + '/' + link
                
                authors = "Unknown"
                dd = dt.find_next_sibling('dd')
                if dd:
                    authors = dd.get_text(strip=True)
                
                papers.append(PaperData(
                    title=title,
                    authors=authors,
                    url=link,
                    pdf_url=link.replace("html", "pdf") if "html" in link else None
                ))
            return papers

        else:
            # MiniConf site (e.g. iccv.thecvf.com/Conferences/2025)
            # 2025 Structure might use a Table
            # <tr> <td> <a href="...">Title</a> ... <div class="indented"><i>Authors</i></div> </td> </tr>
            
            rows = soup.find_all('tr')
            found_rows = False
            for row in rows:
                # We expect a link in the first (or main) td
                tds = row.find_all('td')
                if not tds: continue
                
                # Usually the content is in the second or first TD depending on layout
                # Let's search inside the row for the anchor and author div
                
                a_tag = row.find('a')
                if not a_tag: continue
                
                href = a_tag.get('href')
                if not href: continue
                
                # Check if it looks like a paper link? 
                # The user provided example href: https://deepayan137.github.io/papers/...
                # So it might be external links!
                
                # Title
                title = a_tag.get_text(strip=True)
                if len(title) < 5: continue
                
                # Authors in div.indented i
                author_div = row.find('div', class_='indented')
                authors = "Unknown"
                if author_div:
                    i_tag = author_div.find('i')
                    if i_tag:
                        authors = i_tag.get_text(" ", strip=True)
                        # Clean up middle dots if present
                        # They might be unicode \u00b7
                        authors = authors.replace('·', ',').replace('&middot;', ',')
                
                # Resolve link
                if not href.startswith('http'):
                    link = urljoin(url, href)
                else:
                    link = href
                    
                papers.append(PaperData(
                    title=title,
                    authors=authors,
                    url=link,
                    pdf_url=None
                ))
                found_rows = True
                
            if found_rows:
                return papers

            # Try list items first (Papers list view)
            lis = soup.find_all('li')
            found_li = False
            for li in lis:
                a_tag = li.find('a')
                if not a_tag: continue
                
                href = a_tag.get('href')
                if not href: continue
                
                # Filter for poster/oral/spotlight
                # or just any link that looks like a paper?
                # On MiniConf papers.html, links usually go to /virtual/YEAR/poster/ID
                if "/poster/" in href or "/oral/" in href or "/spotlight/" in href:
                    title = a_tag.get_text(strip=True)
                    if not href.startswith('http'):
                        link = urljoin(url, href)
                    else:
                        link = href
                    
                    papers.append(PaperData(
                        title=title,
                        authors="Visit Detail Page", # MiniConf list view usually lacks authors
                        url=link,
                        pdf_url=None
                    ))
                    found_li = True
            
            if found_li:
                return papers
                
            # Fallback to Cards (MiniConf Grid view)
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
                    
                subtitle = card.find('div', class_='card-subtitle')
                authors = subtitle.get_text(strip=True) if subtitle else "Unknown"
                
                papers.append(PaperData(
                    title=title,
                    authors=authors,
                    url=link,
                    pdf_url=None
                ))
            return papers
