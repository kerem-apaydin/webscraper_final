from flask import Blueprint, render_template, request
from .scraper.fetcher import PageFetcher
from .scraper.parser import ProductParser
from .scraper.saver import ProductSaver
from .scraper.price_tracker import PriceTracker
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    filter_type = request.args.get('filter')
    supplier_filter = request.args.get('supplier')
    products = []
    suppliers = []
    
    if request.method == 'POST':
        url = request.form.get('url')
        if url:
            base_url = 'https://www.dmo.gov.tr'
            fetcher = PageFetcher(base_url)
            parser = ProductParser(fetcher)
            tracker = PriceTracker()
            saver = ProductSaver()

            links = parser.get_all_product_links(url)
            scraped = []
            failures = []

            with ThreadPoolExecutor(max_workers=10) as executor:
                
                futures = {executor.submit(parser.parse_product, link, failures): link for link in links}
                for fut in as_completed(futures):
                    scraped.extend(fut.result() or [])

            products = tracker.track_changes(scraped)
            saver.save(products)
            tracker.save_current_as_old()

            suppliers = sorted({p['supplier'] for p in products if p.get('supplier')})
            return render_template('index.html', products=products, suppliers=suppliers)

    data_path = Path('products.json')
    if data_path.exists():
        with open('products.json','r',encoding='utf-8') as f:
            all_products = json.load(f)

        q = request.args.get('q','').strip().lower()
        if q:
            all_products = [
                p for p in all_products
                if q in (p.get('title','') + p.get('supplier','') + p.get('product_code','')).lower()
            ]

        sort_by = request.args.get('sort')
        if sort_by == 'price_asc':
            all_products.sort(key=lambda x: x.get('raw_price',0))
        elif sort_by == 'price_desc':
            all_products.sort(key=lambda x: x.get('raw_price',0), reverse=True)

        if supplier_filter:
            products = [p for p in all_products if p.get('supplier') == supplier_filter]
        elif filter_type == 'price_drop':
            products = [
                p for p in all_products
                if p.get('last_change_direction') == 'down'
                and p.get('last_change_recent')
            ]
        elif filter_type == 'suppliers':
            products = [p for p in all_products if p.get('supplier')]
        else:
            products = all_products

        suppliers = sorted({p['supplier'] for p in products if p.get('supplier')})

    return render_template('index.html', products=products, suppliers=suppliers)

@main.route('/product/<product_code>')
def product_detail(product_code):
    product = None
    price_logs = []
    if Path('products.json').exists():
        with open('products.json','r',encoding='utf-8') as f:
            all_products = json.load(f)
            product = next((p for p in all_products if p.get('product_code') == product_code), None)
    if Path('price_history.json').exists():
        with open('price_history.json','r',encoding='utf-8') as f:
            history = json.load(f)
            price_logs = history.get(product_code, [])
    return render_template('product_detail.html', product=product, price_logs=price_logs)
