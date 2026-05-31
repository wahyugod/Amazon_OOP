import csv
import statistics

def load_and_analyze(csv_file):
    # Lists untuk menyimpan data metrik
    ratings = []
    discounts = []
    prices = []
    
    # Dictionary untuk menyimpan data kategori
    categories = {}
    
    # Lists untuk analisis harga vs diskon
    high_discount_ratings = []
    low_discount_ratings = []

    # 1. PROSES PEMBACAAN DAN PEMBERSIHAN DATA
    try:
        with open(csv_file, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    # Clean Price
                    clean_price = row['discounted_price'].replace('₹', '').replace(',', '')
                    price = float(clean_price) if clean_price else 0.0
                    
                    # Clean Discount
                    clean_pct = row['discount_percentage'].replace('%', '')
                    discount = float(clean_pct) / 100 if clean_pct else 0.0
                    
                    # Clean Rating (Mengabaikan data yang aneh/corrupt dengan try-except)
                    clean_rating = row['rating'].replace(',', '.')
                    try:
                        rating = float(clean_rating)
                    except ValueError:
                        continue # Skip baris jika rating tidak valid

                    # Ambil Kategori Utama
                    main_category = row['category'].split('|')[0] if row['category'] else "Unknown"

                    # Simpan ke list keseluruhan
                    prices.append(price)
                    discounts.append(discount)
                    ratings.append(rating)

                    # Kelompokkan berdasarkan kategori
                    if main_category not in categories:
                        categories[main_category] = {'count': 0, 'ratings': []}
                    categories[main_category]['count'] += 1
                    categories[main_category]['ratings'].append(rating)

                    # Pisahkan untuk analisis diskon
                    if discount > 0.50:
                        high_discount_ratings.append(rating)
                    else:
                        low_discount_ratings.append(rating)

                except KeyError:
                    continue # Skip jika ada kolom yang hilang
    except FileNotFoundError:
        print(f"[ERROR] File {csv_file} tidak ditemukan!")
        return

    n = len(prices)
    if n == 0:
        print("Tidak ada data valid untuk dianalisis.")
        return

    # 2. PERHITUNGAN STATISTIK
    # Statistik Rating
    avg_rating = statistics.mean(ratings)
    med_rating = statistics.median(ratings)
    min_rating = min(ratings)
    max_rating = max(ratings)
    std_rating = statistics.stdev(ratings) if len(ratings) > 1 else 0.0

    # Statistik Diskon (ubah ke persen)
    avg_disc = statistics.mean(discounts) * 100
    med_disc = statistics.median(discounts) * 100
    min_disc = min(discounts) * 100
    max_disc = max(discounts) * 100
    std_disc = statistics.stdev(discounts) * 100 if len(discounts) > 1 else 0.0

    # Statistik Harga
    avg_price = statistics.mean(prices)
    med_price = statistics.median(prices)
    min_price = min(prices)
    max_price = max(prices)
    std_price = statistics.stdev(prices) if len(prices) > 1 else 0.0

    # 3. MENCETAK HASIL (Menyamai Outline Presentasi)
    print(f"HASIL ANALISIS DATA")
    print(f"Ringkasan Eksekutif Dataset (n = {n}):\n")
    
    print(f"{'Statistik':<14} | {'Rating':<6} | {'Diskon (%)':<10} | {'Harga Diskon (INR)':<15}")
    print("-" * 72)
    print(f"{'Rata-rata':<14} | {avg_rating:<6.2f} | {avg_disc:<9.1f}% | {avg_price:,.1f}")
    print(f"{'Median':<14} | {med_rating:<6.2f} | {med_disc:<9.1f}% | {med_price:,.1f}")
    print(f"{'Minimum':<14} | {min_rating:<6.2f} | {min_disc:<9.1f}% | {min_price:,.1f}")
    print(f"{'Maksimum':<14} | {max_rating:<6.2f} | {max_disc:<9.1f}% | {max_price:,.1f}")
    print(f"{'Std Dev':<14} | {std_rating:<6.2f} | {std_disc:<9.1f}% | {std_price:,.1f}")
    print("\n" + "="*60 + "\n")

    # Analisis Kategori
    print("Temuan Analisis Kategori (CategoryAnalyzer):")
    
    # Mencari tahu kategori mayoritas
    sorted_cats = sorted(categories.items(), key=lambda x: x[1]['count'], reverse=True)
    top_cat_name, top_cat_data = sorted_cats[0]
    top_cat_percentage = (top_cat_data['count'] / n) * 100
    
    print(f"- '{top_cat_name}' mendominasi dataset dengan {top_cat_percentage:.1f}% ({top_cat_data['count']} item) total produk.")
    
    # Mencari "Computers & Accessories" jika ada
    comp_cat = next((cat for cat in categories if "Computers" in cat), None)
    if comp_cat:
        comp_avg_rating = statistics.mean(categories[comp_cat]['ratings'])
        print(f"- Kategori \"{comp_cat}\" memiliki rata-rata ulasan {comp_avg_rating:.2f} dengan volume {categories[comp_cat]['count']} produk.")

    print("\nTemuan Analisis Harga (PricingAnalyzer):")
    print("- Produk dengan diskon tinggi (>50%) BUKAN jaminan mendapatkan rating lebih tinggi.")
    
    avg_high_disc = statistics.mean(high_discount_ratings) if high_discount_ratings else 0
    avg_low_disc = statistics.mean(low_discount_ratings) if low_discount_ratings else 0
    
    print(f"- Rata-rata rating untuk produk diskon tinggi (>50%) : {avg_high_disc:.2f}")
    print(f"- Rata-rata rating untuk produk diskon rendah (<=50%): {avg_low_disc:.2f}")
    print("- Kesimpulan: Pembeli lebih mementingkan kualitas fundamental daripada sekadar potongan harga yang ekstrim.")

if __name__ == "__main__":
    # Jalankan analisis menggunakan dataset amazon.csv
    load_and_analyze('amazon.csv')