import csv
from collections import Counter, defaultdict

import matplotlib.pyplot as plt


def clean_float(value, default=0.0):
	if value is None:
		return default
	text = str(value).strip()
	if not text:
		return default
	text = text.replace("₹", "").replace(",", "")
	text = text.replace("%", "")
	try:
		return float(text)
	except ValueError:
		return default


def load_data(csv_file):
	products = []

	with open(csv_file, mode="r", encoding="utf-8") as file:
		reader = csv.DictReader(file)
		for row in reader:
			rating_text = row.get("rating", "")
			try:
				rating = float(str(rating_text).replace(",", ".")) if str(rating_text).strip() else 0.0
			except ValueError:
				rating = 0.0

			discount_percentage = clean_float(row.get("discount_percentage", "")) / 100.0
			discounted_price = clean_float(row.get("discounted_price", ""))
			main_category = row.get("category", "Unknown")
			main_category = main_category.split("|")[0] if main_category else "Unknown"

			products.append(
				{
					"product_id": row.get("product_id", ""),
					"product_name": row.get("product_name", ""),
					"main_category": main_category,
					"discounted_price": discounted_price,
					"discount_percentage": discount_percentage,
					"rating": rating,
				}
			)

	return products


def plot_category_distribution(products, top_n=10):
	category_counter = Counter(product["main_category"] for product in products)
	top_categories = category_counter.most_common(top_n)

	categories = [category for category, _ in top_categories][::-1]
	counts = [count for _, count in top_categories][::-1]

	plt.figure(figsize=(11, 7))
	bars = plt.barh(categories, counts, color="#2E86C1")
	plt.title("Distribusi Kategori Produk", fontsize=15, fontweight="bold")
	plt.xlabel("Jumlah Produk")
	plt.ylabel("Kategori")
	plt.grid(axis="x", linestyle="--", alpha=0.3)

	for bar, count in zip(bars, counts):
		plt.text(bar.get_width() + 5, bar.get_y() + bar.get_height() / 2, str(count), va="center", fontsize=10)

	plt.tight_layout()
	plt.savefig("kategori_produk.png", dpi=200, bbox_inches="tight")
	if plt.get_backend().lower() != "agg":
		plt.show()
	plt.close()

	print("\n[VISUALISASI] Distribusi Kategori Produk")
	for category, count in top_categories[:3]:
		print(f"- {category}: {count} produk")
	if top_categories:
		top_category, top_count = top_categories[0]
		print(f"Insight: Pasar paling masif berada pada kategori {top_category.lower()} dan kategori teratas lainnya.")


def plot_discount_vs_rating(products):
	discounts = [product["discount_percentage"] * 100 for product in products]
	ratings = [product["rating"] for product in products]

	plt.figure(figsize=(11, 7))
	plt.scatter(discounts, ratings, alpha=0.35, s=28, c=discounts, cmap="viridis", edgecolors="none")
	plt.title("Scatter Plot: Persentase Diskon vs Rating Produk", fontsize=15, fontweight="bold")
	plt.xlabel("Persentase Diskon (%)")
	plt.ylabel("Rating")
	plt.xlim(0, 100)
	plt.ylim(1, 5)
	plt.grid(True, linestyle="--", alpha=0.25)
	cbar = plt.colorbar()
	cbar.set_label("Persentase Diskon (%)")

	plt.tight_layout()
	plt.savefig("diskon_vs_rating.png", dpi=200, bbox_inches="tight")
	if plt.get_backend().lower() != "agg":
		plt.show()
	plt.close()

	print("\n[VISUALISASI] Scatter Plot Diskon vs Rating")
	if ratings:
		rating_bucket = [rating for rating in ratings if 3.8 <= rating <= 4.5]
		print(f"- Sebaran rating dominan berada pada rentang 3.8 - 4.5 ({len(rating_bucket)} produk)")

		high_rating_low_discount = [
			product
			for product in products
			if product["rating"] >= 4.8 and product["discount_percentage"] <= 0.30
		]
		print(
			"- Produk dengan rating 5 sempurna mayoritas cenderung memiliki diskon di bawah 30%"
			if high_rating_low_discount
			else "- Tidak ditemukan pola dominan rating 5 dengan diskon di bawah 30% pada data ini."
		)

	print("- Insight: Tidak terlihat korelasi linear positif yang kuat antara besaran diskon dan kenaikan rating produk.")


def main():
	csv_file = "amazon.csv"
	products = load_data(csv_file)

	if not products:
		print("Tidak ada data yang bisa divisualisasikan.")
		return

	plot_category_distribution(products, top_n=10)
	plot_discount_vs_rating(products)


if __name__ == "__main__":
	main()
