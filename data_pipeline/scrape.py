import requests

from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sqlite3

base_url = "https://books.toscrape.com/"

scraped_books = []
GBP_TO_INR = 105.50

categories = {
    "Mystery": "https://books.toscrape.com/catalogue/category/books/mystery_3/index.html",
    "Poetry": "https://books.toscrape.com/catalogue/category/books/poetry_23/index.html",
    "Science Fiction": "https://books.toscrape.com/catalogue/category/books/science-fiction_16/index.html"
}

for category_name, category_url in categories.items():

    page_number = 1

    while True:

        response = requests.get(category_url, timeout=10)

        print(
            category_name,
            "Page:",
            page_number,
            "Status:",
            response.status_code
        )

        soup = BeautifulSoup(response.text, "html.parser")

        books = soup.find_all(
            "article",
            class_="product_pod"
        )

        print("Books found:", len(books))

        for book in books:
            title = book.h3.a["title"]
            price_raw = book.find(
                "p",
                class_="price_color"
            ).text

            try:
                price_gbp = float(
                    price_raw.replace("£", "")
                             .replace("Â", "")
                             .strip()
             )
            except (ValueError, TypeError):
                print(f"Skipping invalid price for: {title}")
                continue

            price_inr = round(price_gbp * GBP_TO_INR, 2)

            rating_text = book.find(
                 "p",
                  class_="star-rating"
            )["class"][1]

            rating_map = {
                "One": 1,
                "Two": 2,
                "Three": 3,
                "Four": 4,
                "Five": 5
            }

            rating = rating_map.get(rating_text)

            if rating is None:
                print(f"Skipping invalid rating for: {title}")
                continue

            availability = book.find(
                "p",
                class_="instock"
            ).text.strip()
            in_stock = "In stock" in availability

            scraped_books.append({
                "title": title,
                "price": price_raw,
                "price_gbp": price_gbp,
                "price_inr": price_inr,
                "star_rating": rating_text,
                "rating": rating,
                "availability": availability,
                "in_stock": in_stock,
                "category": category_name
            })

        next_page = soup.find(
            "li",
            class_="next"
        )

        if next_page is None:
            break

        next_url = next_page.a["href"]

        category_url = urljoin(
            category_url,
            next_url
        )

        page_number += 1

print("Total books scraped:", len(scraped_books))
print(scraped_books[0])
# Create SQLite database

conn = sqlite3.connect("books.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT NOT NULL UNIQUE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS books (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    price_gbp REAL,
    price_inr REAL,
    rating INTEGER,
    in_stock BOOLEAN,
    category_id INTEGER,
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
)
""")

conn.commit()

print("Database tables created successfully.")
# Insert categories

categories = [
    "Mystery",
    "Poetry",
    "Science Fiction"
]

for category in categories:
    cursor.execute(
        "INSERT OR IGNORE INTO categories (category_name) VALUES (?)",
        (category,)
    )

conn.commit()

print("Categories inserted successfully.")
# Insert books
cursor.execute("DELETE FROM books")
for book in scraped_books:

    cursor.execute(
        "SELECT category_id FROM categories WHERE category_name = ?",
        (book["category"],)
    )

    category_id = cursor.fetchone()[0]

    cursor.execute("""
        INSERT INTO books (
            title,
            price_gbp,
            price_inr,
            rating,
            in_stock,
            category_id
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        book["title"],
        book["price_gbp"],
        book["price_inr"],
        book["rating"],
        book["in_stock"],
        category_id
    ))

conn.commit()

print("Books inserted successfully.")
# Verify database

cursor.execute("SELECT COUNT(*) FROM books")

book_count = cursor.fetchone()[0]

print("Books in database:", book_count)
conn.close()