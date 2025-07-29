from urllib.parse import urljoin, urlencode, urlparse, parse_qs
import re
from bs4 import BeautifulSoup
import requests

class PageFetcher:
    def __init__(self, base_url):
        self.base_url = base_url

    def get_soup(self, url, retries=3, timeout=(5, 10)):
        for attempt in range(1, retries + 1):
            try:
                print(f"Sayfa indiriliyor: {url} (Deneme {attempt})")
                response = requests.get(url, timeout=timeout)
                response.raise_for_status()
                return BeautifulSoup(response.content, "html.parser")
            except Exception as e:
                print(f"get_soup hatası {url} → {e}")
                if attempt == retries:
                    return None

class ProductParser:
    def __init__(self, fetcher):
        self.fetcher = fetcher

    def get_all_product_links(self, start_url):
        links = []
        visited_pages = set()
        page = 1
        while True:
            parts = urlparse(start_url)
            query = parse_qs(parts.query)
            query['p'] = [str(page)]
            page_url = f"{parts.scheme}://{parts.netloc}{parts.path}?{urlencode(query, doseq=True)}"
            if page_url in visited_pages:
                break
            visited_pages.add(page_url)

            soup = self.fetcher.get_soup(page_url)
            if not soup:
                break

            for a in soup.select('a[href*="/Katalog/Urun/Detay/"]'):
                href = a.get('href')
                if href:
                    full = urljoin(self.fetcher.base_url, href)
                    if full not in links:
                        links.append(full)

            nums = [int(a.get_text(strip=True)) for a in soup.select('ul.pagination li a') if a.get_text(strip=True).isdigit()]
            max_page = max(nums) if nums else page
            if page >= max_page:
                break
            page += 1

        return links

    def normalize_price(self, text):
        if not text:
            return None
        return float(text.replace('.', '').replace(',', '.').split(' ')[0])

    def extract_vat_rate(self, soup):
        lbl = soup.select_one("label:-soup-contains('Vergi(KDV) Oranı:')")
        if lbl:
            m = re.search(r"(\d+)%", lbl.text)
            if m:
                return int(m.group(1)) / 100.0
        return None

    def parse_product(self, url, failures=None):
        visited = set()
        all_products = []

        def parse_one(link, override_supplier=None, override_price=None):
            if link in visited:
                return
            visited.add(link)

            soup = self.fetcher.get_soup(link)
            if not soup:
                if failures is not None:
                    failures.append(link)
                return

            box = soup.select_one('#single-product')
            if not box:
                return

            def safe_sel(sel):
                el = box.select_one(sel)
                return el.get_text(strip=True) if el else None

            img_el = box.select_one('div.gallery-holder img')
            img_url = urljoin(self.fetcher.base_url, img_el['src']) if img_el else None

            raw = self.normalize_price(safe_sel('.price-current'))
            price_v = self.normalize_price(safe_sel('.price-prev'))
            vat = self.extract_vat_rate(soup)

            if raw is None and price_v and vat:
                raw = round(price_v * (1 + vat), 2)
            elif price_v is None and raw and vat:
                price_v = round(raw / (1 + vat), 2)

            code = safe_sel("label:-soup-contains('DMO Ürün Kodu:') + span")
            title = safe_sel('div.title span')
            sup = safe_sel('.availability a')
            if override_supplier:
                sup = override_supplier
            if override_price:
                raw = override_price
                if vat:
                    price_v = round(override_price / (1 + vat), 2)

            if sup and not sup.lower().startswith('tedarikçi listesi'):
                all_products.append({
                    'title': title,
                    'supplier': sup,
                    'raw_price': raw,
                    'price_v': price_v,
                    'image': img_url,
                    'product_code': code,
                    'url': link
                })

            for item in soup.select('section#digerTedarikcilerTab li.list-group-item'):
                nm = item.select_one('span')
                pr = item.select_one('b')
                ln = item.select_one('a[href]')
                name = nm.get_text(strip=True) if nm else None
                price_txt = pr.get_text(strip=True) if pr else None
                alt_link = urljoin(self.fetcher.base_url, ln['href']) if ln else None
                alt_price = self.normalize_price(price_txt)
                if name and alt_link and not name.lower().startswith('tedarikçi listesi'):
                    parse_one(alt_link, override_supplier=name, override_price=alt_price)

        try:
            parse_one(url)
        except Exception as e:
            if failures is not None:
                failures.append(url)
        return all_products
