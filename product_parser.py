import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://www.dmo.gov.tr"

def parse_product_detail(url):
    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.content, "html.parser")
        body = soup.select_one("#single-product")
        if not body:
            print(f"[!] Ürün gövdesi bulunamadı: {url}")
            return None

        #Başlık
        raw_title = body.select_one(".body .title a")
        title = raw_title.get_text(strip=True).replace("\xa0", " ") if raw_title else None

        #Tedarikçi
        supplier = body.select_one(".availability a")
        supplier = supplier.get_text(strip=True) if supplier else None

        #Fiyatlar
        price_with_tax_el = body.select_one(".price-prev")
        price_without_tax_el = body.select_one(".price-current")

        def parse_price(price_el):
            if price_el:
                raw = price_el.get_text(strip=True).split()[0]
                clean = raw.replace(".", "").replace(",", ".")
                try:
                    return float(clean)
                except ValueError:
                    return None
            return None

        price_with_tax = parse_price(price_with_tax_el)
        price_without_tax = parse_price(price_without_tax_el)

   
        dmo_code_el = body.select_one("label:contains('DMO Ürün Kodu:') + span")
        dmo_code = dmo_code_el.get_text(strip=True) if dmo_code_el else None

       
        unit_el = body.select_one("label:contains('Ölçü Birimi:') + span")
        unit = unit_el.get_text(strip=True) if unit_el else None


        #Görsel
        img_el = body.select_one("div#owl-single-product img")
        img_src = urljoin(BASE_URL, img_el.get("src")) if img_el else None

        return {
            "url": url,
            "title": title,
            "supplier": supplier,
            "price_with_tax": price_with_tax,
            "price_without_tax": price_without_tax,
            "dmo_code": dmo_code,
            "unit": unit,
            "warranty": warranty,
            "tax_rate": tax_rate,
            "image_url": img_src
        }

    except Exception as e:
        print(f"[X] Hata oluştu ({url}): {e}")
        return None
