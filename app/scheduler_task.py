import json
from .scraper.fetcher import PageFetcher
from .scraper.parser import ProductParser
from .scraper.saver import ProductSaver
from .scraper.price_tracker import PriceTracker
from pathlib import Path

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
        failed_links = []

        for product in old_products:
            url = product.get("url")
            if url and url not in visited:
                visited.add(url)
                try:
                    new_items = parser.parse_product(url, failures=failed_links)
                    all_products.extend(new_items)
                except Exception as e:
                    print(f"Hata ({url}): {e}")

        if failed_links:
            print(f"{len(failed_links)} başarısız link tekrar deneniyor...")
            retry_failures = []
            for retry_url in failed_links:
                try:
                    retried = parser.parse_product(retry_url, failures=retry_failures)
                    all_products.extend(retried)
                except Exception as e:
                    print(f"Tekrar hatası ({retry_url}): {e}")
                    retry_failures.append(retry_url)

            with open("failed_links.json", "w", encoding="utf-8") as f:
                json.dump(retry_failures, f, ensure_ascii=False, indent=4)
            print(f"{len(retry_failures)} başarısız link kaydedildi: failed_links.json")

        all_products = tracker.track_changes(all_products)
        saver.save(all_products)
        tracker.save_current_as_old()

        print(f"Tarama tamamlandı. {len(all_products)} ürün işlendi.")

    except Exception as e:
        print(f"Genel hata: {e}")
