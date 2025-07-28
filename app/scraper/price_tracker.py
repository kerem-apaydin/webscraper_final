import json, re

class PriceTracker:
    def __init__(self, old_file='products_old.json'):
        self.old_file = old_file
        self.old_data = self._load_old_data()

    def normalize_code(self, code):
        if not code:
            return None
        return re.sub(r"\s+", "", code.strip())

    def get_old_product(self, product_code):
        code_norm = self.normalize_code(product_code)
        for item in self.old_data:
            if self.normalize_code(item.get("product_code")) == code_norm:
                return item
        return None

    def _load_old_data(self):
        try:
            with open(self.old_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def track_changes(self, new_products):
        for product in new_products:
            old = self.get_old_product(product.get("product_code"))
            if old:
                if old.get("price_with_vat") != product.get("price_with_vat"):
                    product["old_price_with_vat"] = old.get("price_with_vat")
                if old.get("price_without_vat") != product.get("price_without_vat"):
                    product["old_price_without_vat"] = old.get("price_without_vat")
        return new_products

    def save_current_as_old(self, source_file="products.json"):
        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                all_products = json.load(f)
        except Exception as e:
            print(f"[save_current_as_old] Ürünler okunamadı: {e}")
            all_products = []

        with open(self.old_file, 'w', encoding='utf-8') as f:
            json.dump(all_products, f, ensure_ascii=False, indent=4)

        print(f"{len(all_products)} ürün yedek olarak kaydedildi: {self.old_file}")