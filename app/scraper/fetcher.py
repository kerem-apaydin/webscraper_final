import requests
from bs4 import BeautifulSoup

class PageFetcher:
    def __init__(self, base_url):
        self.base_url = base_url

    def get_soup(self, url):
        print(f"Sayfa indiriliyor: {url}")
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.content, "html.parser")
