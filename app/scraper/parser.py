from urllib.parse import urljoin, urlencode, urlparse, parse_qs
import re

class ProductParser:
    def __init__(self, fetcher):
        self.fetcher = fetcher

    def get_all_product_links(self, start_url, max_pages=30):
        links = []
        visited_pages = set()

        for page in range(1, max_pages + 1):
            url_parts = urlparse(start_url)
            query = parse_qs(url_parts.query)
            query["p"] = [str(page)]
            new_query = urlencode(query, doseq=True)
            page_url = f"{url_parts.scheme}://{url_parts.netloc}{url_parts.path}?{new_query}"

            if page_url in visited_pages:
                break
            visited_pages.add(page_url)

            try:
                soup = self.fetcher.get_soup(page_url)

                if page == 1:
                    pagination = soup.select("ul.pagination li a")
                    sayfa_sayilari = [
                        int(a.get_text(strip=True))
                        for a in pagination
                        if a.get_text(strip=True).isdigit()
                    ]
                    if sayfa_sayilari:
                        max_pages = max(sayfa_sayilari)

                for a in soup.select('a[href*="/Katalog/Urun/Detay/"]'):
                    href = a.get('href')
                    if href:
                        full = urljoin(self.fetcher.base_url, href)
                        if full not in links:
                            links.append(full)
            except Exception as e:
                print(f"Hata ({page_url}): {e}")
                break

        return links

    def normalize_price(self, price_text):
        if not price_text:
            return None
        return float(price_text.replace(".", "").replace(",", ".").split(" ")[0])

    def extract_vat_rate(self, soup):
        label = soup.select_one("label:-soup-contains('Vergi(KDV) Oranı:')")
        if label:
            match = re.search(r"(\d+)\s?%", label.text)
            if match:
                return int(match.group(1)) / 100.0
        return None

    def parse_product_detail_and_alternatives(self, url):
        visited = set()
        all_products = []

        def parse_one(link, override_supplier=None, override_price=None):
            if link in visited:
                return
            visited.add(link)

            soup = self.fetcher.get_soup(link)
            box = soup.select_one("#single-product")

            def safe_sel(selector):
                el = box.select_one(selector)
                return el.get_text(strip=True) if el else None

            image = box.select_one("div.gallery-holder img")
            image_url = urljoin(self.fetcher.base_url, image["src"]) if image else None

            price_with_vat = self.normalize_price(safe_sel(".price-current"))
            price_without_vat = self.normalize_price(safe_sel(".price-prev"))

            vat_rate = self.extract_vat_rate(soup)

            if price_with_vat is None and price_without_vat and vat_rate:
                price_with_vat = round(price_without_vat * (1 + vat_rate), 2)
            elif price_without_vat is None and price_with_vat and vat_rate:
                price_without_vat = round(price_with_vat / (1 + vat_rate), 2)

            product_code = safe_sel("label:-soup-contains('DMO Ürün Kodu:') + span")
            title = safe_sel("div.title span")
            supplier = safe_sel(".availability a")

            if override_supplier:
                supplier = override_supplier
            if override_price:
                price_with_vat = override_price
                if vat_rate:
                    price_without_vat = round(override_price / (1 + vat_rate), 2)

            if supplier and not supplier.lower().startswith("tedarikçi listesi"):
                product_data = {
                    "title": title,
                    "supplier": supplier,
                    "price_with_vat": price_with_vat,
                    "price_without_vat": price_without_vat,
                    "image": image_url,
                    "product_code": product_code,
                    "url": link
                }
                all_products.append(product_data)

            diger_tedarikciler = soup.select("section#digerTedarikcilerTab li.list-group-item")
            for item in diger_tedarikciler:
                name_el = item.select_one("span")
                price_el = item.select_one("b")
                link_el = item.select_one("a[href]")

                name = name_el.get_text(strip=True) if name_el else None
                price_text = price_el.get_text(strip=True) if price_el else None
                alt_link = urljoin(self.fetcher.base_url, link_el["href"]) if link_el else None
                alt_price = self.normalize_price(price_text)

                if name and alt_link and not name.lower().startswith("tedarikçi listesi"):
                    parse_one(alt_link, override_supplier=name, override_price=alt_price)

        parse_one(url)
        return all_products
