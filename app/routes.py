from flask import Blueprint, render_template, request, redirect, url_for
from .scraper.fetcher import PageFetcher
from .scraper.parser import ProductParser
from .scraper.saver import ProductSaver
from .scraper.price_tracker import PriceTracker

import json
from pathlib import Path

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    filter_type = request.args.get("filter")
    supplier_filter = request.args.get("supplier")
    products = []
    suppliers = set()
    products_old = []

    if Path("products_old.json").exists():
        with open("products_old.json", "r", encoding="utf-8") as f:
            products_old = json.load(f)

    if request.method == 'POST':
        url = request.form.get('url')
        if url:
            base_url = "https://www.dmo.gov.tr"
            fetcher = PageFetcher(base_url)
            parser = ProductParser(fetcher)
            tracker = PriceTracker()
            saver = ProductSaver()

            try:
                links = parser.get_all_product_links(url, max_pages=10)
                scraped = []
                for link in links:
                    scraped.extend(parser.parse_product_detail_and_alternatives(link))

                products = tracker.track_changes(scraped)
                saver.save(products)
                tracker.save_current_as_old()

              
                with open("products_temp.json", "w", encoding="utf-8") as f:
                    json.dump(products, f, ensure_ascii=False, indent=4)

               
                return render_template('index.html', products=products, suppliers=[])

            except Exception as e:
                print(f"Hata: {e}")
                return render_template('index.html', products=[], suppliers=[])

   
    data_path = Path("products.json")
    if data_path.exists():
        with open(data_path, "r", encoding="utf-8") as f:
            all_products = json.load(f)
            for p in all_products:
                if p.get("supplier"):
                    suppliers.add(p["supplier"])
            if filter_type == "suppliers":
                products = [p for p in all_products if p.get("supplier")]
            elif supplier_filter:
                products = [p for p in all_products if p.get("supplier") == supplier_filter]
            else:
                products = all_products

    return render_template('index.html', products=products, suppliers=sorted(suppliers), products_old=products_old)
