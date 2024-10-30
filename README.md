# Data Pipeline for Vectorizing and Querying Unstructured Text Data

## Overview

This project implements a scalable data pipeline that ingests, preprocesses, vectorizes, and queries unstructured text data (product reviews) using embeddings and language models. It includes an API that allows querying based on a text prompt, retrieves similar records from the database, and generates responses using a Retriever-Augmented Generation (RAG) approach.

The pipeline is designed to:

- Ingest raw review data from a JSON file into a PostgreSQL database.
- Preprocess the data by cleaning and normalizing the text.
- Generate embeddings for the cleaned text using a Sentence Transformer model.
- Store embeddings in the database with support for vector operations.
- Provide an API for querying similar reviews and generating responses using OpenAI's GPT models.

This README provides detailed step-by-step instructions to set up, run, and understand the project, making it accessible even to those unfamiliar with Python or the underlying concepts.

## Table of Contents

- Prerequisites
- Setup Instructions
    - Clone the Repository
        2. Set Up a Python Virtual Environment
        3. Install Dependencies
        4. Configure Environment Variables
        5. Set Up PostgreSQL Database
        6. Enable the vector Extension
- Running the Data Pipeline
    1. Data Ingestion
    2. Data Preprocessing
    3. Embeddings Generation
- Running the API Server
- Testing the Pipeline and API
- Understanding the Code
    - Scripts Overview
    - Detailed Code Explanation
- Notes for Presentation
- Conclusion

## Prerequisites

- Python 3.8 or higher
- PostgreSQL database with the vector extension installed
- OpenAI API key (for language generation)
- Git (for cloning the repository)

## Setup Instructions

1. Clone the Repository

```bash
git clone https://github.com/wtrevena/LLM_Data_Engineer_Pre-Assignment.git
cd LLM_Data_Engineer_Pre-Assignment
```

2. Set Up a Python Virtual Environment

It's recommended to use a virtual environment to manage dependencies.
```bash
python3 -m venv venv
source venv/bin/activate
```

Activate the virtual environment:

- On macOS/Linux:
```bash
source venv/bin/activate
```

- On Windows:
```bash
venv\Scripts\activate
```

3. Install Dependencies

Install all required Python packages using pip:

```bash
pip install -r requirements.txt
```

4. Configure Environment Variables

Create a .env file in the root directory to store environment variables:

```bash
touch .env
```

Add the following variables to the .env file:

```dotenv
DATABASE_URL=postgresql://username:password@localhost:5432/llm_data_engineer
OPENAI_API_KEY=your_openai_api_key_here
```

Replace username and password with your PostgreSQL credentials.
Replace your_openai_api_key_here with your actual OpenAI API key.

5. Set Up PostgreSQL Database

Ensure PostgreSQL is installed and running on your machine.

Create a new database named llm_data_engineer:

```bash
createdb llm_data_engineer
```

Verify that the database is created:

```bash
psql -l
```

6. Enable the vector Extension

The vector extension is required for vector operations in PostgreSQL.

Connect to the database:

```bash
psql llm_data_engineer
```

Install the vector extension:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Verify the extension is installed:

```sql
\dx
```

Exit the PostgreSQL shell:

```sql
\q
```

## Running the Data Pipeline

1. Data Ingestion

Ingest the raw data from the JSON file into the PostgreSQL database.

```bash
python scripts/data_ingestion.py
```

What It Does: Reads the reviews.json file, converts it into a DataFrame, and stores it in the raw_reviews table in the database.

2. Data Preprocessing

Preprocess the data by cleaning the text and removing duplicates.

```bash
python scripts/data_preprocessing.py
```

What It Does: Cleans the text data by converting it to lowercase, removing punctuation, and extra whitespace. Stores the cleaned data in the cleaned_reviews table.

3. Embeddings Generation

Generate embeddings for the cleaned review texts and store them in the database.

```bash
python scripts/embeddings_generation.py
```

What It Does: Uses a Sentence Transformer model to generate embeddings for each review. Stores these embeddings in the review_embeddings table with vector support for efficient similarity search.

Running the API Server

Start the FastAPI server to enable querying.

```bash
python scripts/api_server.py
```

What It Does: Starts an API server that accepts POST requests to the /query endpoint. It retrieves similar reviews based on the input query and generates a response using OpenAI's GPT model.

Testing the Pipeline and API

Run the unit and integration tests to ensure everything works correctly.

```bash
python -m unittest discover tests
```

Expected Output:

```markdown

    .....
    ----------------------------------------------------------------------
    Ran 5 tests in X.XXXs

    OK
```

Testing the API Manually

Using curl:

```bash
curl -X POST "http://localhost:8000/query" \
-H "Content-Type: application/json" \
-d '{"query_text": "Looking for a product with excellent build quality.", "top_k": 5, "temperature": 0.7}'
```

Using a Python Script:

```python
import requests

    url = "http://localhost:8000/query"
    payload = {
        "query_text": "Looking for a product with excellent build quality.",
        "top_k": 5,
        "temperature": 0.7
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        print("API response:", response.json())
    else:
        print(f"Failed to get a valid response. Status code: {response.status_code}")
    print("Response content:", response.text)
```

Expected Response:

A JSON array containing the most similar reviews and a generated response. For example:

```json
[
    {
        "review_id":"1",
        "review_text":"This product exceeded my expectations. The build quality is excellent.",
        "similarity_score":1.758762240409851,
        "generated_response":"Based on the context provided, it seems that there is a product mentioned that has excellent build quality. However, there are mixed reviews about its overall performance, as one user expressed dissatisfaction due to it stopping working after a week and not matching the description. If you're specifically looking for a product with excellent build quality, you might want to consider the one that was highlighted for its build quality, but also take into account the concerns regarding its performance. It may be worth researching additional reviews or similar products to ensure you find one that meets your expectations."
    },
    {
        "review_id":"3",
        "review_text":"Average quality, but good value for the price.",
        "similarity_score":1.4659703075885773,
        "generated_response":null
    },
    {
        "review_id":"4",
        "review_text":"Excellent customer service and fast shipping!",
        "similarity_score":1.3217270970344543,
        "generated_response":null
    },
    {
        "review_id":"2",
        "review_text":"Not satisfied with the performance. It stopped working after a week.",
        "similarity_score":1.243279218673706,
        "generated_response":null
    },
    {
        "review_id":"5",
        "review_text":"The product does not match the description.",
        "similarity_score":1.2292590290307999,
        "generated_response":null
    }
]
```

## Understanding the Code
### Scripts Overview

- scripts/data_ingestion.py: Ingests raw data into the database.
- scripts/data_preprocessing.py: Cleans and preprocesses the data.
- scripts/embeddings_generation.py: Generates embeddings and stores them in the database.
- scripts/api_server.py: Runs the API server for querying and generating responses.
- scripts/config.py: Contains configuration variables.
- scripts/utils.py: Utility functions, including logging setup.
- tests/test_pipeline.py: Contains unit and integration tests.
