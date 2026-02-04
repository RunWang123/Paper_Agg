from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup

@dataclass
class PaperData:
    title: str
    authors: str
    url: str
    url: str
    pdf_url: Optional[str] = None
    tags: Optional[str] = None # Comma-separated tags

class EventScraper(ABC):
    def __init__(self, conference_name: str, year: int):
        self.conference_name = conference_name
        self.year = year

    @abstractmethod
    def scrape(self, url: str) -> List[PaperData]:
        pass

    def get_soup(self, url: str):
        import time
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                # Use comprehensive browser headers to avoid bot detection
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Cache-Control': 'max-age=0',
                }
                
                # Add a small delay between requests to be respectful
                if attempt > 0:
                    time.sleep(retry_delay * attempt)
                
                response = requests.get(url, headers=headers, timeout=30, verify=False)
                response.raise_for_status()
                return BeautifulSoup(response.content, 'html.parser')
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 403 and attempt < max_retries - 1:
                    print(f"Got 403 error for {url}, retrying in {retry_delay * (attempt + 1)}s...")
                    continue
                print(f"Error fetching {url}: {e}")
                return None
            except Exception as e:
                print(f"Error fetching {url}: {e}")
                return None
        
        return None
