import json
import time
from scraper import collect_all_product_links
from product_parser import parse_product_detail

def main():
    start_url = input("🔗 Başlangıç linkini girin: ").strip()

    print("[i] Ürün linkleri toplanıyor...")
    product_links = collect_all_product_links(start_url)
    print(f"[✓] {len(product_links)} ürün linki bulundu.\n")

    all_products = []
    for i, link in enumerate(product_links, 1):
        print(f"[{i}/{len(product_links)}] {link} işleniyor...")
        data = parse_product_detail(link)
        if data:
            all_products.append(data)
        time.sleep(0.7)

    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(all_products, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Tüm veriler output.json dosyasına kaydedildi ({len(all_products)} ürün).")

if __name__ == "__main__":
    main()
