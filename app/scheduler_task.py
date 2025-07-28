from .scraper.fetcher import PageFetcher
from .scraper.parser import ProductParser
from .scraper.saver import ProductSaver
from .scraper.price_tracker import PriceTracker

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

            products.append(product)

        products = tracker.track_changes(products)
        saver.save(products)
        tracker.save_current_as_old(products)
        print("\u2705 Otomatik scraping tamamlandı.")
    except Exception as e:
        print(f"\u274C Hata: {e}")
