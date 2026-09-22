import sqlite3
import pandas as pd
# Connect to database
conn = sqlite3.connect("books.db")

cursor = conn.cursor()


# File to save SQL queries and outputs
output_file = open("query_results.txt", "w")


def save_query_output(query_number, query, results):
    print(f"\nQuery {query_number} Results:")

    output_file.write(f"Query {query_number}:\n")
    output_file.write(query + "\n")
    output_file.write("Output:\n")

    for row in results:
        print(row)
        output_file.write(str(row) + "\n")

    output_file.write("\n")


# ============================================================
# Query 1: SELECT + WHERE
# ============================================================

query1 = """
SELECT title, price_gbp
FROM books
WHERE price_gbp > 40
"""

cursor.execute(query1)

results = cursor.fetchall()

save_query_output(1, query1, results)


# ============================================================
# Query 2: ORDER BY
# ============================================================

query2 = """
SELECT title, price_gbp
FROM books
ORDER BY price_gbp DESC
"""

cursor.execute(query2)

results = cursor.fetchall()

save_query_output(2, query2, results)


# ============================================================
# Query 3: LIMIT
# ============================================================

query3 = """
SELECT title, price_inr
FROM books
ORDER BY price_inr DESC
LIMIT 5
"""

cursor.execute(query3)

results = cursor.fetchall()

save_query_output(3, query3, results)


# ============================================================
# Query 4: DISTINCT
# ============================================================

query4 = """
SELECT DISTINCT rating
FROM books
ORDER BY rating
"""

cursor.execute(query4)

results = cursor.fetchall()

save_query_output(4, query4, results)


# ============================================================
# Query 5: IN
# ============================================================

query5 = """
SELECT title, rating
FROM books
WHERE rating IN (4, 5)
ORDER BY rating DESC
"""

cursor.execute(query5)

results = cursor.fetchall()

save_query_output(5, query5, results)


# ============================================================
# Query 6: JOIN
# ============================================================

query6 = """
SELECT
    b.title,
    b.price_gbp,
    c.category_name
FROM books AS b
JOIN categories AS c
    ON b.category_id = c.category_id
ORDER BY b.title
LIMIT 10
"""

cursor.execute(query6)

results = cursor.fetchall()

save_query_output(6, query6, results)

# ============================================================
# Pandas: Read SQL query results into DataFrames
# ============================================================

query1_df = pd.read_sql(query1, conn)

print("\nPandas DataFrame - Query 1:")
print(query1_df)


query6_df = pd.read_sql(query6, conn)


print("\nPandas DataFrame - Query 6:")
print(query6_df)

# ============================================================
# Pandas: Reproduce SQL JOIN using pd.merge()
# ============================================================

books_df = pd.read_sql(
    "SELECT * FROM books",
    conn
)

categories_df = pd.read_sql(
    "SELECT * FROM categories",
    conn
)


pandas_join = (
    books_df
    .merge(
        categories_df,
        on="category_id",
        how="inner"
    )
    [["title", "price_gbp", "category_name"]]
    .sort_values("title")
    .head(10)
    .reset_index(drop=True)
)

print("\nPandas JOIN using merge:")
print(pandas_join)


# ============================================================
# Close files and database
# ============================================================

output_file.close()
conn.close()

print("\nAll SQL queries executed successfully.")
print("Query strings and outputs saved to query_results.txt")