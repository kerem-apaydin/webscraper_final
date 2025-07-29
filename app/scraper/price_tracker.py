import os
import json
from datetime import datetime, timedelta

class PriceTracker:
    def __init__(self):
        self.data_file = "products.json"
        self.history_file = "price_history.json"

    def track_changes(self, new_products):
        history = {}
        if os.path.exists(self.history_file):
            with open(self.history_file, "r", encoding="utf-8") as f:
                history = json.load(f)

        for product in new_products:
            code = product.get("product_code")
            hist = history.get(code, [])
            if hist:
                last = hist[-1]
                product["last_change_date"] = last.get("date")
                if len(hist) >= 2:
                    prev = hist[-2]
                    direction = "up" if last.get("price_v", 0) > prev.get("price_v", 0) else "down"
                    product["last_change_direction"] = direction
                    try:
                        dt = datetime.strptime(last.get("date"), "%Y-%m-%d %H:%M:%S")
                        product["last_change_recent"] = (datetime.now() - dt) < timedelta(hours=24)
                    except Exception:
                        product["last_change_recent"] = False
                        product["last_change_direction"] = "stand"
        return new_products

    def save_current_as_old(self):
        if not os.path.exists(self.data_file):
            return
        with open(self.data_file, 'r', encoding='utf-8') as f:
            current_data = json.load(f)

        history_data = {}
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history_data = json.load(f)

        for product in current_data:
            code = product.get('product_code')
            if not code:
                continue
            entry = {
                'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'price_v': product.get('price_v')
            }
            history_data.setdefault(code, [])
            if not history_data[code] or history_data[code][-1].get('price_v') != entry['price_v']:
                history_data[code].append(entry)

        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, ensure_ascii=False, indent=4)
