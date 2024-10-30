# scripts/data_ingestion.py

import json
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.types import Integer, Text, Float
from config import DATABASE_URL
from utils import get_logger
import os

# Initialize logger for logging messages
logger = get_logger('data_ingestion')

def load_data_to_dataframe(json_file_path):
    """
    Load data from a JSON file into a pandas DataFrame.

    Args:
        json_file_path (str): The path to the JSON file containing the data.

    Returns:
        pd.DataFrame: A DataFrame containing the data from the JSON file.
    """
    data = []
    # Open the JSON file and read each line
    with open(json_file_path, 'r') as file:
        for line in file:
            # Parse each line as JSON and append to the data list
            data.append(json.loads(line))
    # Convert the list of data into a DataFrame
    dataframe = pd.DataFrame(data)
    return dataframe

def ingest_data_to_db(dataframe, table_name, engine):
    """
    Ingest a DataFrame into a specified table in the database.

    Args:
        dataframe (pd.DataFrame): The DataFrame to ingest.
        table_name (str): The name of the table to create or replace.
        engine (Engine): The SQLAlchemy engine connected to the database.
    """
    # Write the DataFrame to the SQL table
    dataframe.to_sql(
        table_name,
        engine,
        if_exists='replace',  # Replace the table if it already exists
        index=False,          # Do not include the DataFrame index as a column
        dtype={               # Specify data types for each column
            'review_id': Text,
            'product_id': Text,
            'review_text': Text,
            'rating': Float,
            'timestamp': Integer
        }
    )
    logger.info(f"Data ingested into table {table_name}.")

if __name__ == '__main__':
    # Create a database engine using the configured DATABASE_URL
    engine = create_engine(DATABASE_URL)
    # Construct the path to the JSON file containing the reviews
    json_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'reviews.json')
    # Load the data into a DataFrame
    df = load_data_to_dataframe(json_file_path)
    # Ingest the DataFrame into the 'raw_reviews' table in the database
    ingest_data_to_db(df, 'raw_reviews', engine)
    print("Data ingestion completed successfully.")
