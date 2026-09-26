
# Zepto Data & AI Platform

A single public repository containing three project modules completed as part of the capstone:

- `/data_pipeline` — Books to Scrape data pipeline, SQLite database, SQL analysis, and pandas analysis.
- `/analytics` — Titanic exploratory data analysis, classification, imbalance handling, model tuning, and fare regression.
- `/support_assistant` — Zepto policy RAG assistant using Sentence Transformers, ChromaDB, LangGraph, Pydantic, and FastAPI.

## Repository Structure

```text
zepto-data-ai-platform/
├── README.md
├── requirements.txt
├── data_pipeline/
│   ├── README.md
│   ├── requirements.txt
│   ├── scrape.py
│   ├── pipe_line.py
│   ├── books.db
│   └── query_results.txt
├── analytics/
│   ├── README.md
│   ├── requirements.txt
│   ├── 01_eda.ipynb
│   ├── titanic.csv
│   └── best_model_pipeline.joblib
└── support_assistant/
    ├── README.md
    ├── requirements.txt
    ├── rag.py
    ├── main.py
    ├── Dockerfile
    └── docs/
```

## Setup

Dependencies are maintained separately for each module.

### Module 1 — Data Pipeline

From the `data_pipeline` directory:

```bash
python3 -m pip install -r requirements.txt
```

### Module 2 — Analytics

From the `analytics` directory:

```bash
python3 -m pip install -r requirements.txt
```

The Analytics requirements include the packages used by the notebook, including `imbalanced-learn` for SMOTE.

### Module 3 — Support Assistant

From the repository root:

```bash
conda activate zepto-support
cd support_assistant
python -m pip install -r requirements.txt
```

The support assistant supports `MOCK_LLM=1`, so a paid LLM service is not required for evaluation.

## Running the Modules End to End

### 1. Data Pipeline

From `data_pipeline/`:

```bash
python3 scrape.py
python3 pipe_line.py
```

Expected completed dataset:

- Mystery: 32 books
- Poetry: 19 books
- Science Fiction: 16 books
- Total: 67 books

Generated outputs include `books.db` and `query_results.txt`.

### 2. Titanic Analytics

Open:

```text
analytics/01_eda.ipynb
```

Run the notebook from top to bottom.

The workflow includes:

- Dataset loading and inspection
- Missing-value analysis
- Data cleaning
- Outlier analysis
- Univariate and bivariate analysis
- Survival analysis
- Classification models
- Class-imbalance handling
- SMOTE
- Random Forest hyperparameter tuning with GridSearchCV
- Fare regression
- Model saving and reloading

The saved classification pipeline is:

```text
analytics/best_model_pipeline.joblib
```

### 3. Zepto Support Assistant

From the repository root:

```bash
export MOCK_LLM=1
uvicorn support_assistant.main:app --host 0.0.0.0 --port 7860
```

The API exposes:

```text
POST /ask
```

Example request:

```bash
curl -X POST "http://127.0.0.1:7860/ask" \
  -H "Content-Type: application/json" \
  -d '{"query":"How long does Zepto delivery take?"}'
```

The application indexes eight policy documents into ChromaDB, retrieves relevant context, routes requests through LangGraph, and returns a validated Pydantic response.

### Docker

Docker build and runtime testing were successfully completed locally.

The image `zepto-support` was built successfully, the container was started on port `7860`, and the `/ask` endpoint was verified with both a policy retrieval query and a non-retrieval query.

## Design Decisions

### Data Pipeline

The pipeline uses a normalized SQLite schema with separate category and book tables. Scraped values are cleaned into structured fields, including GBP and INR prices, numeric star ratings, and a boolean stock indicator. SQL queries demonstrate filtering, sorting, limiting, distinct values, range filtering, and joins. Pandas reproduces relational analysis through `merge`.

### Analytics

The Titanic workflow keeps the analysis reproducible inside one notebook. Missing values are handled during preprocessing, categorical variables are encoded through the modeling pipeline, and class imbalance is investigated using baseline, class-weighted, and SMOTE approaches. Random Forest hyperparameters are tuned with GridSearchCV, and the selected classification pipeline is saved as a joblib artifact. Fare prediction is treated separately as a regression task.

### Support Assistant

The support assistant uses a local policy corpus and ChromaDB for vector retrieval. Sentence Transformers provides embeddings, LangGraph separates intent classification, retrieval/answer generation, and direct-answer routing, Pydantic validates the response structure, and FastAPI exposes the workflow through `/ask`. Mock mode avoids requiring a paid LLM service during evaluation.

## Documentation

Each module contains its own README with module-specific details, implementation notes, and execution guidance.

## Submission

This repository is intended to be submitted as one public GitHub repository containing all three modules at the repository root.

## Git Workflow

Git workflow used for the project:

1. Development work was completed on feature branches.
2. Changes were committed with descriptive commit messages.
3. The `final-submission-readme` branch was used for final submission documentation.
4. The `final-submission-readme` branch was merged into `main`.
5. Final fixes were committed on `main` and pushed to the GitHub repository.
6. The final repository is maintained on the `main` branch.

The final submission therefore demonstrates feature-branch development, multiple commits, a merge into `main`, and subsequent final fixes.