import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse
import time

BASE_URL = "https://www.dmo.gov.tr"

def get_total_pages(soup):
    pagination = soup.select_one("ul.pagination")
    if not pagination:
        return 1
    last_page_link = pagination.find_all("a")[-2] 
    href = last_page_link.get("href", "")
    parsed = parse_qs(urlparse(href).query)
    return int(parsed.get("p", [1])[0])

def get_product_links_from_page(soup):
    product_links = []
    product_anchors = soup.select("div.product-item-holder a[href^='/Katalog/Urun/Detay/']")
    for a in product_anchors:
        href = a.get("href")
        if href:
            full_url = urljoin(BASE_URL, href)
            product_links.append(full_url)
    return product_links

def construct_page_url(base_url, page):
    parsed_url = urlparse(base_url)
    query_params = parse_qs(parsed_url.query)
    query_params["p"] = [str(page)]
    new_query = urlencode(query_params, doseq=True)
    return urlunparse(parsed_url._replace(query=new_query))

def collect_all_product_links(start_url):
    print(f"[i] Başlangıç URL: {start_url}")
    all_links = []

    res = requests.get(start_url)
    soup = BeautifulSoup(res.content, "html.parser")
    total_pages = get_total_pages(soup)
    print(f"[i] Toplam sayfa: {total_pages}")

    for page in range(1, total_pages + 1):
        paged_url = construct_page_url(start_url, page)
        print(f"[+] Sayfa {page}: {paged_url}")
        res = requests.get(paged_url)
        soup = BeautifulSoup(res.content, "html.parser")
        product_links = get_product_links_from_page(soup)
        all_links.extend(product_links)
        time.sleep(0.7) 

    return list(set(all_links))

