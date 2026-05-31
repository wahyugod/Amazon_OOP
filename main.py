import csv
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import List, Dict

# ==========================================
# 1. MODELS (Data Representation)
# ==========================================
@dataclass
class Product:
    product_id: str
    name: str
    main_category: str
    discounted_price: float
    discount_percentage: float
    rating: float
    rating_count: int

    def __post_init__(self):
        # Validasi Data (Encapsulation)
        if self.discounted_price < 0:
            raise ValueError(f"Harga tidak boleh negatif pada produk {self.product_id}")
        if not (0.0 <= self.rating <= 5.0):
            raise ValueError(f"Rating harus berada di antara 0 dan 5.0 pada produk {self.product_id}")
        if self.discount_percentage < 0 or self.discount_percentage > 1:
            raise ValueError(f"Diskon harus berupa persentase 0.0 - 1.0 pada produk {self.product_id}")

    def is_highly_rated(self) -> bool:
        return self.rating >= 4.0 and self.rating_count > 1000

    def get_revenue_estimate(self) -> float:
        # Estimasi kasar pendapatan berdasarkan jumlah rating (asumsi 1 rating = 1 penjualan minimal)
        return self.discounted_price * self.rating_count

    def __str__(self) -> str:
        return f"[{self.product_id}] {self.name[:40]}... | Rating: {self.rating} | Diskon: {self.discount_percentage*100:.0f}%"


# ==========================================
# 2. REPOSITORY (Data Access & Cleaning)
# ==========================================
class SalesRepository:
    def __init__(self):
        self._products: List[Product] = []

    def load_csv(self, path: str) -> None:
        """Membaca file CSV, melakukan pembersihan data, dan memasukkan ke List of Product"""
        try:
            with open(path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        # Data Cleaning: Membersihkan simbol mata uang dan koma
                        clean_price = row['discounted_price'].replace('₹', '').replace(',', '')
                        discounted_price = float(clean_price) if clean_price else 0.0

                        # Data Cleaning: Membersihkan simbol %
                        clean_pct = row['discount_percentage'].replace('%', '')
                        discount_pct = float(clean_pct) / 100 if clean_pct else 0.0

                        # Data Cleaning: Rating kadang berisi string aneh seperti '|'
                        clean_rating = row['rating'].replace(',', '.')
                        try:
                            rating = float(clean_rating)
                        except ValueError:
                            rating = 0.0 # Default jika rating corrupt

                        # Data Cleaning: Rating count
                        clean_rc = row['rating_count'].replace(',', '')
                        rating_count = int(clean_rc) if clean_rc else 0

                        # Ambil kategori utama (kategori sebelum tanda '|')
                        main_category = row['category'].split('|')[0] if row['category'] else "Unknown"

                        # Instansiasi Objek Product
                        product = Product(
                            product_id=row['product_id'],
                            name=row['product_name'],
                            main_category=main_category,
                            discounted_price=discounted_price,
                            discount_percentage=discount_pct,
                            rating=rating,
                            rating_count=rating_count
                        )
                        self._products.append(product)
                    except ValueError as e:
                        # Skip row yang datanya terlalu corrupt tapi log error-nya
                        # print(f"Skipping row {row['product_id']} due to error: {e}")
                        continue
            print(f"[INFO] Berhasil memuat {len(self._products)} produk dari {path}")
        except FileNotFoundError:
            print(f"[ERROR] File {path} tidak ditemukan!")

    def get_all(self) -> List[Product]:
        return self._products

    def filter_by_category(self, category: str) -> List[Product]:
        return [p for p in self._products if category.lower() in p.main_category.lower()]


# ==========================================
# 3. ANALYZERS (Business Logic / Services)
# ==========================================
class BaseSalesAnalyzer(ABC):
    def __init__(self, products: List[Product]):
        self._data = products

    @abstractmethod
    def analyze(self) -> Dict:
        pass


class CategoryAnalyzer(BaseSalesAnalyzer):
    def analyze(self) -> Dict:
        return {
            "total_products": len(self._data),
            "top_categories": self.get_top_categories(),
            "category_rating_summary": self.get_category_rating_summary(),
            "highest_rating_category": self.get_highest_rating_category()
        }

    def get_top_categories(self, limit: int = 5) -> List[tuple]:
        category_counts = {}
        for p in self._data:
            category_counts[p.main_category] = category_counts.get(p.main_category, 0) + 1
        
        # Sortir descending berdasarkan jumlah produk
        sorted_categories = sorted(category_counts.items(), key=lambda item: item[1], reverse=True)
        return sorted_categories[:limit]

    def get_category_rating_summary(self) -> List[tuple]:
        category_stats = {}
        for p in self._data:
            if p.main_category not in category_stats:
                category_stats[p.main_category] = {"total_rating": 0.0, "count": 0}
            category_stats[p.main_category]["total_rating"] += p.rating
            category_stats[p.main_category]["count"] += 1

        summary = []
        for category, stats in category_stats.items():
            avg_rating = stats["total_rating"] / stats["count"] if stats["count"] else 0.0
            summary.append((category, stats["count"], avg_rating))

        return sorted(summary, key=lambda item: item[2], reverse=True)

    def get_highest_rating_category(self):
        rating_summary = self.get_category_rating_summary()
        if not rating_summary:
            return None
        return rating_summary[0]


class PricingAnalyzer(BaseSalesAnalyzer):
    def analyze(self) -> Dict:
        return self.discount_vs_rating()

    def discount_vs_rating(self) -> Dict:
        high_discount = [p for p in self._data if p.discount_percentage > 0.5]
        low_discount = [p for p in self._data if 0.0 < p.discount_percentage <= 0.5]
        no_discount = [p for p in self._data if p.discount_percentage == 0.0]

        def get_avg_rating(products_list):
            if not products_list:
                return 0.0
            return sum(p.rating for p in products_list) / len(products_list)

        return {
            "high_discount (>50%)": {
                "count": len(high_discount),
                "avg_rating": get_avg_rating(high_discount)
            },
            "low_discount (<=50%)": {
                "count": len(low_discount),
                "avg_rating": get_avg_rating(low_discount)
            },
            "no_discount (0%)": {
                "count": len(no_discount),
                "avg_rating": get_avg_rating(no_discount)
            }
        }


def run_pytest_suite() -> int:
    try:
        import pytest
    except ImportError:
        print("[ERROR] Pytest belum terpasang di environment ini.")
        return 1

    print("\n[Menjalankan Pytest...]")
    return pytest.main(["-q"])


# ==========================================
# 4. MAIN APP (CLI Interface)
# ==========================================
def main():
    print("=============================================")
    print("   AMAZON SALES ANALYTICS - OOP PIPELINE     ")
    print("=============================================")
    
    repo = SalesRepository()
    repo.load_csv("amazon.csv")
    products = repo.get_all()

    if not products:
        print("[ERROR] Tidak ada data yang bisa dianalisis. Keluar dari program.")
        return

    while True:
        print("\nPilih Mode Analisis:")
        print("1. Analisis Kategori (Category Analyzer)")
        print("2. Analisis Harga & Diskon (Pricing Analyzer)")
        print("3. Filter Produk Berdasarkan Kategori Terbaik")
        print("4. Testing Pytest")
        print("5. Keluar")
        
        pilihan = input("> Input Pilihan (1/2/3/4/5): ")

        if pilihan == '1':
            print("\n[Menjalankan CategoryAnalyzer...]")
            analyzer = CategoryAnalyzer(products)
            hasil = analyzer.analyze()
            print(f"Total Produk Dianalisis: {hasil['total_products']}")
            print("Top 5 Kategori Terbanyak:")
            for rank, (cat, count) in enumerate(hasil['top_categories'], 1):
                print(f"{rank}. {cat} ({count} produk)")
            print("\nRata-rata Rating per Kategori (urut tertinggi):")
            for rank, (cat, count, avg_rating) in enumerate(hasil['category_rating_summary'][:5], 1):
                print(f"{rank}. {cat} | {count} produk | Rata-rata Rating: {avg_rating:.2f}")

            if hasil['highest_rating_category']:
                best_cat, best_count, best_avg = hasil['highest_rating_category']
                print(f"\nKesimpulan: Kategori dengan rating tertinggi adalah '{best_cat}' dengan rata-rata rating {best_avg:.2f} dari {best_count} produk.")

        elif pilihan == '2':
            print("\n[Menjalankan PricingAnalyzer...]")
            analyzer = PricingAnalyzer(products)
            hasil = analyzer.analyze()
            print("Hasil Analisis Pengaruh Diskon Terhadap Rating:")
            for kategori, data in hasil.items():
                print(f"- {kategori.ljust(20)}: {data['count']} produk | Rata-rata Rating: {data['avg_rating']:.2f}")
            print("\nKesimpulan: Produk dengan diskon yang lebih wajar atau tanpa diskon kadang memiliki kualitas rating yang lebih solid.")

        elif pilihan == '3':
            keyword = input("Masukkan nama kategori (misal: Electronics, Computers): ")
            filtered_products = repo.filter_by_category(keyword)
            print(f"\n[INFO] Ditemukan {len(filtered_products)} produk untuk kategori '{keyword}'.")
            if filtered_products:
                print("Menampilkan 5 produk teratas dari pencarian Anda:")
                for p in filtered_products[:5]:
                    print(p)

        elif pilihan == '4':
            result = run_pytest_suite()
            if result == 0:
                print("[INFO] Semua test pytest lulus.")
            else:
                print(f"[WARN] Ada test yang gagal atau pytest selesai dengan kode: {result}")
                    
        elif pilihan == '5':
            print("Terima kasih. Program selesai.")
            break
        else:
            print("Pilihan tidak valid, coba lagi.")

if __name__ == "__main__":
    main()