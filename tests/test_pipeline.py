# tests/test_pipeline.py

import unittest
from sqlalchemy import create_engine, text
from scripts.config import DATABASE_URL
import requests

class TestPipeline(unittest.TestCase):
    def setUp(self):
        # Initialize the database engine
        self.engine = create_engine(DATABASE_URL)
        # API endpoint URL
        self.api_url = 'http://localhost:8000/query'
        # Sample query for testing the API
        self.sample_query = {
            "query_text": "Great battery life and camera quality",
            "top_k": 3,
            "temperature": 0.5
        }

    def test_database_connection(self):
        # Test if the database connection is successful
        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            connected = True
        except Exception as e:
            print(f"Database connection error: {e}")
            connected = False
        self.assertTrue(connected, "Database connection failed.")

    def test_data_ingestion(self):
        # Test if data has been ingested into 'raw_reviews' table
        with self.engine.connect() as connection:
            result = connection.execute(text("SELECT COUNT(*) FROM raw_reviews")).scalar()
        self.assertGreater(result, 0, "Data ingestion failed, 'raw_reviews' table is empty.")

    def test_data_preprocessing(self):
        # Test if data has been preprocessed and stored in 'cleaned_reviews' table
        with self.engine.connect() as connection:
            result = connection.execute(text("SELECT COUNT(*) FROM cleaned_reviews")).scalar()
        self.assertGreater(result, 0, "Data preprocessing failed, 'cleaned_reviews' table is empty.")

    def test_embeddings_generation(self):
        # Test if embeddings have been generated and stored in 'review_embeddings' table
        with self.engine.connect() as connection:
            result = connection.execute(text("SELECT COUNT(*) FROM review_embeddings")).scalar()
        self.assertGreater(result, 0, "Embeddings generation failed, 'review_embeddings' table is empty.")

    def test_api_response(self):
        # Test if the API server is running and responding correctly
        try:
            response = requests.post(self.api_url, json=self.sample_query, timeout=5)
            self.assertEqual(response.status_code, 200, "API response status code is not 200.")
            data = response.json()
            self.assertIsInstance(data, list, "API response is not a list.")
            self.assertGreater(len(data), 0, "API response list is empty.")
        except requests.exceptions.ConnectionError:
            self.fail("Could not connect to the API server. Ensure it is running before running tests.")

if __name__ == '__main__':
    unittest.main()
