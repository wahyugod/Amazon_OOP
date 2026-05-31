import csv

import pytest

from main import CategoryAnalyzer, PricingAnalyzer, Product, SalesRepository


@pytest.fixture
def sample_products():
    return [
        Product("P1", "Mouse", "Computers", 100.0, 0.10, 4.5, 1500),
        Product("P2", "Keyboard", "Computers", 200.0, 0.20, 4.2, 1200),
        Product("P3", "Shirt", "Clothing", 50.0, 0.00, 4.0, 500),
        Product("P4", "Book", "Books", 30.0, 0.60, 4.8, 900),
    ]


def test_product_creation_valid():
    product = Product("P1", "Mouse", "Computers", 100.0, 0.10, 4.5, 1500)
    assert product.product_id == "P1"
    assert product.main_category == "Computers"


def test_product_negative_price_raises():
    with pytest.raises(ValueError):
        Product("P1", "Mouse", "Computers", -1.0, 0.10, 4.5, 1500)


def test_product_invalid_rating_raises():
    with pytest.raises(ValueError):
        Product("P1", "Mouse", "Computers", 100.0, 0.10, 5.5, 1500)


def test_product_invalid_discount_raises():
    with pytest.raises(ValueError):
        Product("P1", "Mouse", "Computers", 100.0, 1.5, 4.5, 1500)


def test_is_highly_rated_true():
    product = Product("P1", "Mouse", "Computers", 100.0, 0.10, 4.5, 1501)
    assert product.is_highly_rated() is True


def test_is_highly_rated_false_due_to_rating():
    product = Product("P1", "Mouse", "Computers", 100.0, 0.10, 3.9, 1501)
    assert product.is_highly_rated() is False


def test_is_highly_rated_false_due_to_count():
    product = Product("P1", "Mouse", "Computers", 100.0, 0.10, 4.5, 1000)
    assert product.is_highly_rated() is False


def test_revenue_estimate():
    product = Product("P1", "Mouse", "Computers", 100.0, 0.10, 4.5, 10)
    assert product.get_revenue_estimate() == 1000.0


def test_repository_filter_by_category_exact_match():
    repo = SalesRepository()
    repo._products = [
        Product("P1", "Mouse", "Computers", 100.0, 0.10, 4.5, 10),
        Product("P2", "Shirt", "Clothing", 50.0, 0.00, 4.0, 5),
    ]
    result = repo.filter_by_category("Computers")
    assert len(result) == 1
    assert result[0].product_id == "P1"


def test_repository_filter_by_category_case_insensitive():
    repo = SalesRepository()
    repo._products = [Product("P1", "Mouse", "Computers", 100.0, 0.10, 4.5, 10)]
    result = repo.filter_by_category("computers")
    assert len(result) == 1


def test_repository_filter_by_category_partial_match():
    repo = SalesRepository()
    repo._products = [Product("P1", "Mouse", "Computers&Accessories", 100.0, 0.10, 4.5, 10)]
    result = repo.filter_by_category("Accessories")
    assert len(result) == 1


def test_category_analyzer_total_products(sample_products):
    analyzer = CategoryAnalyzer(sample_products)
    result = analyzer.analyze()
    assert result["total_products"] == 4


def test_category_analyzer_top_categories(sample_products):
    analyzer = CategoryAnalyzer(sample_products)
    result = analyzer.analyze()
    assert result["top_categories"][0][0] == "Computers"
    assert result["top_categories"][0][1] == 2


def test_category_analyzer_rating_summary_sorted_desc(sample_products):
    analyzer = CategoryAnalyzer(sample_products)
    result = analyzer.analyze()
    assert result["category_rating_summary"][0][0] == "Books"
    assert result["category_rating_summary"][0][2] == pytest.approx(4.8)


def test_category_analyzer_highest_rating_category(sample_products):
    analyzer = CategoryAnalyzer(sample_products)
    result = analyzer.analyze()
    best_category, best_count, best_avg = result["highest_rating_category"]
    assert best_category == "Books"
    assert best_count == 1
    assert best_avg == pytest.approx(4.8)


def test_pricing_analyzer_discount_groups(sample_products):
    analyzer = PricingAnalyzer(sample_products)
    result = analyzer.analyze()
    assert result["high_discount (>50%)"]["count"] == 1
    assert result["low_discount (<=50%)"]["count"] == 2
    assert result["no_discount (0%)"]["count"] == 1


def test_pricing_analyzer_average_rating(sample_products):
    analyzer = PricingAnalyzer(sample_products)
    result = analyzer.analyze()
    assert result["high_discount (>50%)"]["avg_rating"] == pytest.approx(4.8)


def test_load_csv_parses_clean_data(tmp_path):
    csv_path = tmp_path / "sample.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "product_id",
            "product_name",
            "category",
            "discounted_price",
            "discount_percentage",
            "rating",
            "rating_count",
        ])
        writer.writerow(["P1", "Mouse", "Computers|Accessories", "₹1,000", "10%", "4.5", "1,500"])
        writer.writerow(["P2", "Shirt", "Clothing", "₹500", "0%", "4.0", "200"])

    repo = SalesRepository()
    repo.load_csv(str(csv_path))

    assert len(repo.get_all()) == 2
    assert repo.get_all()[0].main_category == "Computers"


def test_load_csv_handles_missing_rating_as_zero(tmp_path):
    csv_path = tmp_path / "sample_missing_rating.csv"
    csv_path.write_text(
        "product_id,product_name,category,discounted_price,discount_percentage,rating,rating_count\n"
        "P1,Mouse,Computers,100,10%,,1500\n",
        encoding="utf-8",
    )

    repo = SalesRepository()
    repo.load_csv(str(csv_path))

    assert len(repo.get_all()) == 1
    assert repo.get_all()[0].rating == 0.0


def test_load_csv_skips_corrupt_discount_percentage(tmp_path):
    csv_path = tmp_path / "sample_corrupt_discount.csv"
    csv_path.write_text(
        "product_id,product_name,category,discounted_price,discount_percentage,rating,rating_count\n"
        "P1,Mouse,Computers,100,abc,4.5,1500\n",
        encoding="utf-8",
    )

    repo = SalesRepository()
    repo.load_csv(str(csv_path))

    assert len(repo.get_all()) == 0


def test_filter_by_category_returns_empty_when_missing(sample_products):
    repo = SalesRepository()
    repo._products = sample_products
    assert repo.filter_by_category("Gaming") == []