from flask import Blueprint, render_template, request, redirect, url_for
from .scraper.fetcher import PageFetcher
from .scraper.parser import ProductParser
from .scraper.saver import ProductSaver
from .scraper.price_tracker import PriceTracker

main = Blueprint('main', __name__)


@main.route('/', methods=['GET'])
def index():
    import json
    from pathlib import Path

    products = []
    if Path("products.json").exists():
        with open("products.json", "r", encoding="utf-8") as f:
            products = json.load(f)

    return render_template('index.html', products=products)

