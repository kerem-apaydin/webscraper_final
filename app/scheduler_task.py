import json
from .scraper.fetcher import PageFetcher
from .scraper.parser import ProductParser
from .scraper.saver import ProductSaver
from .scraper.price_tracker import PriceTracker

def auto_scrape():
    print("Rutin tarama yapılıyor...")

    base_url = "https://www.dmo.gov.tr"
    fetcher = PageFetcher(base_url)
    parser = ProductParser(fetcher)
    tracker = PriceTracker()
    saver = ProductSaver()

    try:
        with open("products.json", "r", encoding="utf-8") as f:
            old_products = json.load(f)

        visited = set()
        all_products = []

        for product in old_products:
            url = product.get("url")
            if url and url not in visited:
                visited.add(url)
                try:
                    new_items = parser.parse_product_detail_and_alternatives(url)
                    all_products.extend(new_items)
                except Exception as e:
                    print(f"Hata ({url}): {e}")

        all_products = tracker.track_changes(all_products)
        saver.save(all_products)
        tracker.save_current_as_old()  

        print(f"Tarama tamamlandı. {len(all_products)} ürün işlendi.")

    except Exception as e:
        print(f"Genel hata: {e}")