# scripts/data_preprocessing.py

import pandas as pd
from sqlalchemy import create_engine
from config import DATABASE_URL
import re
from utils import get_logger

# Initialize logger for logging messages
logger = get_logger('data_preprocessing')

def clean_text(text):
    """
    Clean and normalize text by converting to lowercase,
    removing punctuation, and extra whitespace.

    Args:
        text (str): The text to clean.

    Returns:
        str: The cleaned text.
    """
    text = text.lower()  # Convert text to lowercase
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    return text.strip()  # Remove leading and trailing whitespace

def preprocess_data(engine):
    """
    Preprocess data from the 'raw_reviews' table and store it
    in the 'cleaned_reviews' table.

    Args:
        engine (Engine): The SQLAlchemy engine connected to the database.
    """
    # Read data from the 'raw_reviews' table into a DataFrame
    df = pd.read_sql_table('raw_reviews', con=engine)
    # Remove duplicate reviews based on 'review_id'
    df.drop_duplicates(subset=['review_id'], inplace=True)
    # Remove rows with missing 'review_text'
    df.dropna(subset=['review_text'], inplace=True)
    # Clean the 'review_text' and store it in a new column
    df['cleaned_review_text'] = df['review_text'].apply(clean_text)
    # Write the cleaned data to the 'cleaned_reviews' table
    df.to_sql('cleaned_reviews', engine, if_exists='replace', index=False)
    logger.info("Data preprocessing completed and stored in 'cleaned_reviews' table.")

if __name__ == '__main__':
    # Create a database engine using the configured DATABASE_URL
    engine = create_engine(DATABASE_URL)
    # Preprocess the data
    preprocess_data(engine)
