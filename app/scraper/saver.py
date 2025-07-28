import json
from pathlib import Path

class ProductSaver:
    def __init__(self, filename="products.json"):
        self.filename = filename

    def save(self, new_products):
        existing = []

        if Path(self.filename).exists():
            with open(self.filename, "r", encoding="utf-8") as f:
                try:
                    existing = json.load(f)
                except json.JSONDecodeError:
                    existing = []

        def normalize_code(product):
            return (product.get("product_code") or "").replace(" ", "").strip()

        combined = {normalize_code(p): p for p in existing}

        for product in new_products:
            code = normalize_code(product)
            combined[code] = product

        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(list(combined.values()), f, ensure_ascii=False, indent=4)

        print(f"{len(new_products)} ürün eklendi/güncellendi: {self.filename}")
