# Books Data Pipeline

## Project Overview

This project is an end-to-end data pipeline that scrapes book information from Books to Scrape, cleans and transforms the data, stores the data in a normalized SQLite database, and performs SQL and pandas analysis.

The pipeline collects books from three categories:

* Mystery
* Poetry
* Science Fiction

A total of 67 books are scraped.

## Project Structure

```text
masai project/
└── data_pipeline/
    ├── pipe_line.py
    ├── README.md
    ├── scrape.py
    ├── books.db
    └── query_results.txt
```

## Requirements

* Python 3
* requests
* BeautifulSoup4
* pandas
* SQLite3

## Installation

Install the required Python packages using:

```bash
python3 -m pip install requests beautifulsoup4 pandas
```

SQLite3 is included with standard Python installations.

## How to Run

Open the terminal and move into the `data_pipeline` folder:

```bash
cd "masai project/data_pipeline"
```

### Step 1: Run the scraper

```bash
python3 scrape.py
```

The scraper:

1. Visits the selected book categories.
2. Handles category pagination.
3. Extracts book information.
4. Cleans prices and ratings.
5. Converts GBP prices to INR.
6. Stores the cleaned data in SQLite.

The fixed conversion rate used is:

```text
1 GBP = 105.50 INR
```

The scraper currently collects 67 books.

### Step 2: Run the SQL and pandas pipeline

After scraping, run:

```bash
python3 pipe_line.py
```

This script:

* Executes SQL queries.
* Saves SQL queries and outputs to `query_results.txt`.
* Loads SQL results into pandas using `pd.read_sql()`.
* Reproduces the SQL JOIN using pandas `merge()`.

## Data Cleaning

### Price

The raw price is provided as a GBP currency string.

The currency symbol and encoding artifact are removed before converting the value to a float.

Invalid numeric prices are skipped so that a malformed value does not stop the complete pipeline.

### Rating

Book ratings are provided as text values:

```text
One
Two
Three
Four
Five
```

These are converted to integers:

```text
One   -> 1
Two   -> 2
Three -> 3
Four  -> 4
Five  -> 5
```

Invalid ratings are skipped.

### Availability

The availability text is converted to a Boolean field:

```text
"In stock" -> True
```

Otherwise the value is treated as `False`.

## Currency Conversion

A fixed conversion rate is used as required by the assignment:

```text
1 GBP = 105.50 INR
```

The INR value is calculated as:

```text
price_inr = price_gbp * 105.50
```

The resulting INR value is rounded to two decimal places.

## Database Design

SQLite is used for storage.

The database contains two normalized tables.

### categories

| Column        | Type    | Description          |
| ------------- | ------- | -------------------- |
| category_id   | INTEGER | Primary key          |
| category_name | TEXT    | Unique category name |

### books

| Column      | Type    | Description            |
| ----------- | ------- | ---------------------- |
| book_id     | INTEGER | Primary key            |
| title       | TEXT    | Book title             |
| price_gbp   | REAL    | Price in GBP           |
| price_inr   | REAL    | Converted price in INR |
| rating      | INTEGER | Rating from 1 to 5     |
| in_stock    | BOOLEAN | Availability status    |
| category_id | INTEGER | Foreign key            |

The relationship is:

```text
categories
    |
    | 1-to-many
    |
books
```

The `category_id` column in `books` references `category_id` in `categories`.

## SQL Analysis

The pipeline demonstrates the following SQL operations:

1. `SELECT` with `WHERE`
2. `ORDER BY`
3. `LIMIT`
4. `DISTINCT`
5. `IN`
6. `JOIN`

The SQL query strings and their outputs are automatically saved to:

```text
query_results.txt
```

## Pandas Analysis

SQL query results are loaded into pandas DataFrames using:

```python
pd.read_sql()
```

The SQL JOIN between `books` and `categories` is also reproduced using:

```python
pd.merge()
```

The pandas JOIN produces the same columns and ordering as the SQL JOIN:

* title
* price_gbp
* category_name

## Design Decisions

### Category Selection

Three categories were selected directly from Books to Scrape:

* Mystery
* Poetry
* Science Fiction

This satisfies the requirement to collect data from at least three categories while allowing category information to be captured directly from the category pages.

### Pagination

The scraper follows the `next` pagination link for categories that contain multiple pages.

The resulting collection is:

* Mystery: 32 books
* Poetry: 19 books
* Science Fiction: 16 books

Total:

```text
67 books
```

### Error Handling

The scraper uses request timeouts and catches invalid numeric values during cleaning.

Invalid prices and ratings are skipped rather than stopping the entire pipeline.

### Database Refresh

Before inserting newly scraped books, existing rows in the `books` table are removed.

This prevents duplicate book records when the scraper is run again.

## Output Files

After running the pipeline, the main outputs are:

```text
books.db
query_results.txt
```

`books.db` contains the structured book data.

`query_results.txt` contains the SQL query strings and their outputs.

## End-to-End Execution

Run the following commands from the `data_pipeline` directory:

```bash
python3 scrape.py
python3 pipe_line.py
```

Expected scraper result:

```text
Total books scraped: 67
Books inserted successfully.
Books in database: 67
```

The SQL and pandas analysis then runs successfully using the generated SQLite database.
This project was developed as part of a data engineering assignment.
