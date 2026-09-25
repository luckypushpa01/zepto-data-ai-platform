# Zepto Data & AI Platform

A single public repository containing three project modules completed as part of the capstone:

- `/data_pipeline` — Books to Scrape data pipeline, SQLite database, SQL analysis, and pandas analysis.
- `/analytics` — Titanic exploratory data analysis, classification, imbalance handling, model tuning, and fare regression.
- `/support_assistant` — Zepto policy RAG assistant using Sentence Transformers, ChromaDB, LangGraph, Pydantic, and FastAPI.

## Repository Structure

```text
zepto-data-ai-platform/
├── README.md
├── data_pipeline/
│   ├── README.md
│   ├── requirements.txt
│   ├── scrape.py
│   ├── pipe_line.py
│   ├── books.db
│   └── query_results.txt
├── analytics/
│   ├── README.md
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


## Setup

Dependencies are maintained separately for each module.

### Module 1 — Data Pipeline

From the `data_pipeline` directory:

```bash
python3 -m pip install -r requirements.txt

A single public repository containing three project modules completed as part of the capstone:
- `/data_pipeline` — Books to Scrape data pipeline, SQLite database, SQL analysis, and pandas analysis.
- `/analytics` — Titanic exploratory data analysis, classification, imbalance handling, model tuning, and fare regression.
- `/support_assistant` — Zepto policy RAG assistant using Sentence Transformers, ChromaDB, LangGraph, Pydantic, and FastAPI.

## Repository Structure

```text
zepto-data-ai-platform/
├── README.md
├── data_pipeline/
│   ├── README.md
│   ├── requirements.txt
│   ├── scrape.py
│   ├── pipe_line.py
│   ├── books.db
│   └── query_results.txt
├── analytics/
│   ├── README.md
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
Setup

Dependencies are maintained separately for each module.

Module 1 — Data Pipeline

From the data_pipeline directory:

python3 -m pip install -r requirements.txt

Dependencies include requests, beautifulsoup4, and pandas. SQLite and urllib.parse are provided by Python.

Module 2 — Analytics

Open analytics/01_eda.ipynb in Jupyter Notebook, JupyterLab, or another compatible notebook environment.

The notebook contains the complete EDA, preprocessing, modeling, imbalance handling, hyperparameter tuning, regression analysis, and model saving/reloading workflow.

Module 3 — Support Assistant

Create and activate the recommended environment:

conda create -n zepto-support python=3.12 -y
conda activate zepto-support
cd support_assistant
python -m pip install -r requirements.txt

The support assistant supports a mock mode so that paid LLM services are not required.

Running the Modules End to End
1. Data Pipeline

From data_pipeline/:

python3 scrape.py
python3 pipe_line.py

scrape.py scrapes the required book categories, cleans the records, converts GBP prices to INR using the project conversion rate, and stores the normalized data in SQLite.

pipe_line.py executes the SQL analysis queries and demonstrates pandas analysis using a JOIN.

Expected completed dataset:

Mystery: 32 books
Poetry: 19 books
Science Fiction: 16 books
Total: 67 books

Generated/maintained outputs include:

books.db
query_results.txt
2. Titanic Analytics

Open:

analytics/01_eda.ipynb

Run the notebook cells from top to bottom.

The notebook covers:

Dataset loading and inspection
Missing-value analysis
Data cleaning
Outlier analysis
Univariate and bivariate analysis
Survival analysis
Classification models
Class-imbalance handling
SMOTE
Random Forest hyperparameter tuning with GridSearchCV
Fare regression
Model saving and reloading

The final saved classification pipeline is:

analytics/best_model_pipeline.joblib
3. Zepto Support Assistant

From support_assistant/:

export MOCK_LLM=1
uvicorn main:app --reload

The API exposes:

POST /ask

Example request:

curl -X POST "http://127.0.0.1:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"query":"What is the delivery time?"}'

The application indexes the eight provided policy documents into ChromaDB, retrieves relevant context, routes the request through the LangGraph workflow, and returns a validated Pydantic response.

MOCK_LLM=1 provides a no-paid-service fallback for local execution.

A Dockerfile is included for containerized deployment. Docker build and runtime testing were successfully completed locally. The image `zepto-support` was built successfully, the container was started on port 7860, and the `/ask` endpoint was verified with both a policy retrieval query and a non-retrieval query.

Design Decisions
Data Pipeline

The pipeline uses a normalized SQLite schema with separate category and book tables. Scraped values are cleaned into structured fields, including numeric GBP and INR prices, numeric star ratings, and a boolean stock indicator. SQL queries demonstrate filtering, aggregation, sorting, grouping, and a JOIN. Pandas is then used to reproduce relational analysis through a merge.

Analytics

The Titanic workflow keeps the analysis reproducible inside one notebook. Missing values are handled during preprocessing, categorical variables are encoded through the modeling pipeline, and class imbalance is investigated using baseline, class-weighted, and SMOTE approaches. Random Forest hyperparameters are tuned with GridSearchCV, and the selected pipeline is saved as a joblib artifact. Fare prediction is treated separately as a regression task.

Support Assistant

The support assistant uses a small, local policy corpus and ChromaDB for vector retrieval. Sentence Transformers provides embeddings, while LangGraph separates intent classification, retrieval/answer generation, and direct-answer routing. Pydantic validates the response structure, and FastAPI exposes the workflow through a simple /ask endpoint. Mock mode avoids requiring a paid LLM service during evaluation.

Documentation

Each module contains its own README with module-specific details, implementation notes, and execution guidance.

Submission

This repository is intended to be submitted as one public GitHub repository containing all three modules at the repository root
## Git Workflow
Git workflow used for the project:

1. Development work was completed on feature branches.
2. Changes were committed with descriptive commit messages.
3. The `final-submission-readme` branch was used for final submission documentation.
4. The `final-submission-readme` branch was merged into `main`.
5. Final fixes were committed on `main` and pushed to the GitHub repository.
6. The final repository is maintained on the `main` branch.

The final submission therefore demonstrates feature-branch development, multiple commits, a merge into `main`, and subsequent final fixes.
