import os
import json

class PriceTracker:
    def __init__(self):
        self.old_data_file = "products_old.json"
        self.new_data_file = "products.json"

    def track_changes(self, new_products):
        old_products = {}
        if os.path.exists(self.old_data_file):
            with open(self.old_data_file, "r", encoding="utf-8") as f:
                old_products = {p["product_code"]: p for p in json.load(f)}

        for product in new_products:
            code = product["product_code"]
            old = old_products.get(code)
            if old:
                product["old_price_with_vat"] = old.get("price_with_vat")
                product["old_price_without_vat"] = old.get("price_without_vat")

        return new_products

    def save_current_as_old(self):
        if not os.path.exists(self.new_data_file):
            return

        if os.path.exists(self.old_data_file):
            with open(self.old_data_file, "r", encoding="utf-8") as f:
                old_data = {p["product_code"]: p for p in json.load(f)}
        else:
            old_data = {}

        with open(self.new_data_file, "r", encoding="utf-8") as f:
            current_data = json.load(f)

        updated_data = []
        for product in current_data:
            code = product["product_code"]
            old_product = old_data.get(code)

            if (
                old_product and
                old_product.get("price_without_vat") != product.get("price_without_vat")
            ):
                updated_data.append(old_product)
            elif not old_product:
                updated_data.append(product)

        with open(self.old_data_file, "w", encoding="utf-8") as f:
            json.dump(updated_data, f, ensure_ascii=False, indent=4)

        print(f"{len(updated_data)} ürün yedek olarak kaydedildi: {self.old_data_file}")
