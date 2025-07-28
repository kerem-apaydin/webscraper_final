import json

class ProductSaver:
    def __init__(self, filename="products.json"):
        self.filename = filename

    def save(self, products):
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(products, f, ensure_ascii=False, indent=4)
        print(f"{len(products)} ürün {self.filename} dosyasına kaydedildi.")
