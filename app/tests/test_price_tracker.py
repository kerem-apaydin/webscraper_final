import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.scraper.price_tracker import PriceTracker

def test_track_changes_adds_old_prices(tmp_path):
    old_data = [
        {
            "product_code": "code1",
            "price_with_vat": 100,
            "price_without_vat": 90,
        },
        {
            "product_code": "code2",
            "price_with_vat": 200,
            "price_without_vat": 180,
        },
    ]
    old_file = tmp_path / "old.json"
    old_file.write_text(json.dumps(old_data))

    tracker = PriceTracker(old_file=str(old_file))

    new_products = [
        {
            "product_code": "code1",
            "price_with_vat": 110,
            "price_without_vat": 95,
        },
        {
            "product_code": "code2",
            "price_with_vat": 200,
            "price_without_vat": 190,
        },
        {
            "product_code": "code3",
            "price_with_vat": 300,
            "price_without_vat": 250,
        },
    ]

    updated = tracker.track_changes(new_products)

    p1 = next(p for p in updated if p["product_code"] == "code1")
    assert p1["old_price_with_vat"] == 100
    assert p1["old_price_without_vat"] == 90

    p2 = next(p for p in updated if p["product_code"] == "code2")
    assert "old_price_with_vat" not in p2
    assert p2["old_price_without_vat"] == 180

    p3 = next(p for p in updated if p["product_code"] == "code3")
    assert "old_price_with_vat" not in p3
    assert "old_price_without_vat" not in p3