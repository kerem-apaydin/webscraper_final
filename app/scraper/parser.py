from urllib.parse import urljoin
import re

class ProductParser:
    def __init__(self, fetcher):
        self.fetcher = fetcher

    def get_all_product_links(self, start_url):
        """Return a list of product detail URLs from all pages starting at
        ``start_url``.

        This helper walks pagination links to gather every product link.  It
        looks for anchors that contain ``/Katalog/Urun/Detay/`` in their href
        and follows ``rel="next"`` or common next page selectors if present.
        """

        links = []
        page_url = start_url
        visited_pages = set()

        while page_url and page_url not in visited_pages:
            visited_pages.add(page_url)
            soup = self.fetcher.get_soup(page_url)

            for a in soup.select('a[href*="/Katalog/Urun/Detay/"]'):
                href = a.get('href')
                if not href:
                    continue
                full = urljoin(self.fetcher.base_url, href)
                if full not in links:
                    links.append(full)

            next_link = soup.select_one('a[rel="next"], li.next a, li.pag-next a')
            if next_link and next_link.get('href'):
                page_url = urljoin(self.fetcher.base_url, next_link['href'])
            else:
                break

        return links

    def normalize_price(self, price_text):
        if not price_text:
            return None
        return float(price_text.replace(".", "").replace(",", ".").split(" ")[0])

    def parse_product_detail(self, url):
        soup = self.fetcher.get_soup(url)
        box = soup.select_one("#single-product")

        def safe_sel(selector):
            el = box.select_one(selector)
            return el.get_text(strip=True) if el else None

        image = box.select_one("div.gallery-holder img")
        image_url = urljoin(self.fetcher.base_url, image["src"]) if image else None

        price_with_vat = self.normalize_price(safe_sel(".price-current"))
        price_without_vat = self.normalize_price(safe_sel(".price-prev"))

        product_data = {
            "title": safe_sel("div.title span"),
            "supplier": safe_sel(".availability a"),
            "price_with_vat": price_with_vat,
            "price_without_vat": price_without_vat,
            "image": image_url,
            "product_code": safe_sel("label:contains('DMO Ürün Kodu:') + span"),
            "url": url
        }

        # Alternatif tedarikçileri al
        alternatifler = []
        diger_tedarikciler = soup.select("section#digerTedarikcilerTab li.list-group-item")

        for item in diger_tedarikciler:
            name_el = item.select_one("span")
            price_el = item.select_one("b")
            link_el = item.select_one("a[href]")

            name = name_el.get_text(strip=True) if name_el else None
            price_text = price_el.get_text(strip=True) if price_el else None
            price = self.normalize_price(price_text)
            link = urljoin(self.fetcher.base_url, link_el["href"]) if link_el else None

            if name and price and link:
                alternatifler.append({
                    "supplier": name,
                    "price_with_vat": price,
                    "url": link
                })

        if alternatifler:
            product_data["alternatif_tedarikciler"] = alternatifler

        return product_data
    
    def parse_product_detail_and_alternatives(self, url):
        """
        Ana ürün + varsa alternatif tedarikçili tüm ürünleri döner (zincirleme)
        """
        visited = set()
        all_products = []

        def parse_one(link):
            if link in visited:
                return
            visited.add(link)
            print(f"İşleniyor: {link}")

            soup = self.fetcher.get_soup(link)
            box = soup.select_one("#single-product")

            def safe_sel(selector):
                el = box.select_one(selector)
                return el.get_text(strip=True) if el else None

            image = box.select_one("div.gallery-holder img")
            image_url = urljoin(self.fetcher.base_url, image["src"]) if image else None

            price_with_vat = self.normalize_price(safe_sel(".price-current"))
            price_without_vat = self.normalize_price(safe_sel(".price-prev"))

            product_data = {
                "title": safe_sel("div.title span"),
                "supplier": safe_sel(".availability a"),
                "price_with_vat": price_with_vat,
                "price_without_vat": price_without_vat,
                "image": image_url,
                "product_code": safe_sel("label:contains('DMO Ürün Kodu:') + span"),
                "url": link
            }

            all_products.append(product_data)

            # zincirleme: alternatif tedarikçilere gir
            diger_tedarikciler = soup.select("section#digerTedarikcilerTab li.list-group-item")
            for item in diger_tedarikciler:
                alt_link_el = item.select_one("a[href]")
                alt_link = urljoin(self.fetcher.base_url, alt_link_el["href"]) if alt_link_el else None
                if alt_link:
                    parse_one(alt_link)

        parse_one(url)
        return all_products

