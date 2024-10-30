# scripts/config.py

import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Database connection URL
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres@localhost:5432/llm_data_engineer')

# Name of the embedding model to use
EMBEDDING_MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'

# Batch size for processing data
BATCH_SIZE = 100

# Log file path
LOG_FILE = 'logs/pipeline.log'

# OpenAI API key for language generation
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Temperature setting for the language model
LLM_TEMPERATURE = 0.7
