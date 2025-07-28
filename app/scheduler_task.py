from .scraper.fetcher import PageFetcher
from .scraper.parser import ProductParser
from .scraper.saver import ProductSaver
from .scraper.price_tracker import PriceTracker
from urllib.parse import urljoin

def auto_scrape():
    print("\U0001F553 Otomatik scraping başlatıldı...")

    url = "https://www.dmo.gov.tr/Arama?k=%7C%7CElektronik%7C%7CSunucular+Ve+Yedekleme+%C3%9Cniteleri&p=1"
    base_url = "https://www.dmo.gov.tr"

    fetcher = PageFetcher(base_url)
    parser = ProductParser(fetcher)
    tracker = PriceTracker()
    saver = ProductSaver()

    try:
        links = parser.get_all_product_links(url)
        products = []

        for link in links:
            product = parser.parse_product_detail(link)

            # Alternatif tedarikçileri bul
            soup = fetcher.get_soup(link)
            alternatifler = []
            diger_tedarikciler = soup.select("section#digerTedarikcilerTab li.list-group-item")

            for item in diger_tedarikciler:
                name_el = item.select_one("span")
                price_el = item.select_one("b")
                link_el = item.select_one("a[href]")

                name = name_el.get_text(strip=True) if name_el else None
                price_text = price_el.get_text(strip=True) if price_el else None
                price = float(price_text.replace(".", "").replace(",", ".").split(" ")[0]) if price_text else None
                alt_link = urljoin(fetcher.base_url, link_el["href"]) if link_el else None

                if name and price and alt_link:
                    alternatifler.append({
                        "supplier": name,
                        "price_with_vat": price,
                        "url": alt_link
                    })

            product["alternatif_tedarikciler"] = alternatifler
            products.append(product)

        products = tracker.track_changes(products)
        saver.save(products)
        tracker.save_current_as_old(products)
        print("\u2705 Otomatik scraping tamamlandı.")
    except Exception as e:
        print(f"\u274C Hata: {e}")