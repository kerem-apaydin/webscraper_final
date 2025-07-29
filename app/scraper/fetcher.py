import requests, time, random
from bs4 import BeautifulSoup

class PageFetcher:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()

    def get_soup(self, url, retries=3, timeout=(5, 10)):
        for attempt in range(1, retries + 1):
            try:
                print(f"Sayfa indiriliyor: {url}")
                response = self.session.get(url, timeout=timeout)
                response.raise_for_status()
                time.sleep(random.uniform(0.1, 0.3))
                return BeautifulSoup(response.content, "lxml")
                
            except Exception as e:
                print(f"get_soup hatası {url} → {e}")
                if attempt == retries:
                    return None
