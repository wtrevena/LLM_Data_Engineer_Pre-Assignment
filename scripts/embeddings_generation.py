# scripts/embeddings_generation.py

import pandas as pd
from sqlalchemy import create_engine, text, Table, Column, MetaData, String
from sqlalchemy.types import UserDefinedType
from sqlalchemy.exc import SQLAlchemyError
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from config import DATABASE_URL, EMBEDDING_MODEL_NAME, BATCH_SIZE
from utils import get_logger

# Initialize logger for logging messages
logger = get_logger('embeddings_generation')

class Vector(UserDefinedType):
    """
    Custom SQLAlchemy type for the 'vector' data type used in PostgreSQL.
    """
    def get_col_spec(self):
        # Specify the vector dimension (e.g., 384 for 'all-MiniLM-L6-v2' model)
        return "vector(384)"

    def bind_processor(self, dialect):
        # Process the value before binding to the SQL statement
        def process(value):
            return value  # No processing needed
        return process

    def result_processor(self, dialect, coltype):
        # Process the value after fetching from the database
        def process(value):
            return value  # No processing needed
        return process

def generate_and_store_embeddings(engine):
    """
    Generate embeddings for the cleaned reviews and store them in the database.

    Args:
        engine (Engine): The SQLAlchemy engine connected to the database.
    """
    # Load the pre-trained Sentence Transformer model
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    # Define the table schema for storing embeddings
    metadata = MetaData()
    review_embeddings_table = Table('review_embeddings', metadata,
        Column('review_id', String, primary_key=True),
        Column('embedding', Vector)
    )
    # Create the 'review_embeddings' table if it doesn't exist
    metadata.create_all(engine)

    with engine.begin() as connection:
        # Get the total number of records to process
        total_records = connection.execute(text("SELECT COUNT(*) FROM cleaned_reviews")).scalar()
        offset = 0  # Initialize offset for batching

        # Use tqdm for progress tracking
        with tqdm(total=total_records, desc="Generating embeddings") as pbar:
            while True:
                # Fetch a batch of data from the 'cleaned_reviews' table
                df = pd.read_sql_query(text("""
                    SELECT review_id, cleaned_review_text
                    FROM cleaned_reviews
                    ORDER BY review_id
                    OFFSET :offset
                    LIMIT :limit
                """), connection, params={'offset': offset, 'limit': BATCH_SIZE})

                if df.empty:
                    # Break the loop if no more data is fetched
                    break

                # Generate embeddings for the batch of texts
                embeddings = model.encode(df['cleaned_review_text'].tolist())
                # Convert embeddings to lists and add to the DataFrame
                df['embedding'] = [emb.tolist() for emb in embeddings]

                # Prepare data for insertion into the database
                df_to_insert = df[['review_id', 'embedding']]
                data_to_insert = df_to_insert.to_dict(orient='records')

                # Insert the embeddings into the 'review_embeddings' table
                try:
                    stmt = review_embeddings_table.insert().values(data_to_insert)
                    connection.execute(stmt)
                except SQLAlchemyError as e:
                    logger.error(f"Error inserting data at offset {offset}: {e}")
                    raise  # Re-raise exception after logging

                # Update offset and progress bar
                offset += len(df)
                pbar.update(len(df))
                logger.info(f"Processed batch ending at offset {offset}")

            logger.info("Embeddings generation completed.")

if __name__ == '__main__':
    # Create a database engine using the configured DATABASE_URL
    engine = create_engine(DATABASE_URL)
    # Generate and store embeddings
    generate_and_store_embeddings(engine)
