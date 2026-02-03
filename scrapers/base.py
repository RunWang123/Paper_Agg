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
        try:
            # Use a modern User-Agent to match Chrome browser and avoid basic bot blocks
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
            }
            response = requests.get(url, headers=headers, timeout=30, verify=False)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
