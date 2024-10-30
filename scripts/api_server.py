# scripts/api_server.py

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from sqlalchemy import create_engine, text
from typing import List, Optional
from config import DATABASE_URL, EMBEDDING_MODEL_NAME, OPENAI_API_KEY
import openai
from utils import get_logger
import re

# Initialize logger for logging messages
logger = get_logger('api_server')

# Initialize the FastAPI application
app = FastAPI()

# Create a database engine using the configured DATABASE_URL
engine = create_engine(DATABASE_URL)

# Load the pre-trained Sentence Transformer model
model = SentenceTransformer(EMBEDDING_MODEL_NAME)

# Initialize the OpenAI client with the API key
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Define the request model using Pydantic
class QueryRequest(BaseModel):
    query_text: str          # The user's query text
    top_k: int = 5           # Number of top similar reviews to retrieve
    temperature: float = 0.7 # Temperature for language generation

# Define the response model using Pydantic
class QueryResponse(BaseModel):
    review_id: str                   # ID of the review
    review_text: str                 # Text of the review
    similarity_score: float          # Similarity score with the query
    generated_response: Optional[str] = None  # Generated response (optional)

def generate_response(context_texts, query_text, temperature):
    """
    Generate a response using OpenAI's GPT model based on the context.

    Args:
        context_texts (list): List of review texts to use as context.
        query_text (str): The user's query.
        temperature (float): The temperature for the language model.

    Returns:
        str: The generated response.
    """
    # Construct the messages for the OpenAI chat completion
    messages = [
        {"role": "system", "content": "Use the following context to answer the question."},
        {"role": "user", "content": f"Context: {' '.join(context_texts)}\n\nQuestion: {query_text}"}
    ]
    try:
        # Make a request to the OpenAI API to generate a response
        chat_completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=temperature,
            max_tokens=150,
            n=1,
            stop=None
        )
        # Extract the generated answer from the response
        answer = chat_completion.choices[0].message.content.strip()
        return answer
    except Exception as e:
        # Log the error and raise an HTTPException
        logger.error(f"OpenAI API call failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate response from OpenAI API.")

# Define the API endpoint for querying reviews
@app.post("/query", response_model=List[QueryResponse])
def query_reviews(request: QueryRequest):
    """
    Handle the /query endpoint to retrieve similar reviews and generate a response.

    Args:
        request (QueryRequest): The request containing the query parameters.

    Returns:
        List[QueryResponse]: A list of query responses.
    """
    # Validate 'top_k' to ensure it's a positive integer
    try:
        top_k = int(request.top_k)
        if top_k <= 0:
            raise ValueError
    except ValueError:
        raise HTTPException(status_code=400, detail="'top_k' must be a positive integer.")

    # Generate the embedding for the user's query text
    query_embedding = model.encode([request.query_text])[0]

    # Convert the numpy array to a list for JSON serialization
    query_embedding_list = query_embedding.tolist()
    # Convert the list to a string in PostgreSQL vector format
    query_embedding_str = '[' + ','.join(map(str, query_embedding_list)) + ']'

    # Sanitize 'query_embedding_str' to prevent SQL injection
    if not re.match(r'^\[[-\d., e]+\]$', query_embedding_str):
        raise HTTPException(status_code=400, detail="Invalid characters in embedding.")

    # Construct the SQL query to find similar reviews
    sql = f"""
        SELECT cr.review_id, cr.review_text,
        1 - (re.embedding <#> '{query_embedding_str}'::vector) AS similarity
        FROM review_embeddings re
        JOIN cleaned_reviews cr ON cr.review_id = re.review_id
        ORDER BY re.embedding <#> '{query_embedding_str}'::vector ASC
        LIMIT {top_k}
    """

    try:
        with engine.connect() as connection:
            # Execute the SQL query
            result_proxy = connection.execute(text(sql))
            # Get column names from the result proxy
            columns = result_proxy.keys()
            # Convert the results to a list of dictionaries
            results = [dict(zip(columns, row)) for row in result_proxy.fetchall()]
    except Exception as e:
        # Log the error and raise an HTTPException
        logger.error(f"Database query failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during database query.")

    if not results:
        # If no results are found, raise a 404 error
        raise HTTPException(status_code=404, detail="No matching reviews found.")

    # Extract review texts to use as context
    context_texts = [row['review_text'] for row in results]
    # Generate a response using the context and query
    generated_text = generate_response(context_texts, request.query_text, request.temperature)

    # Build the response data
    response = [
        QueryResponse(
            review_id=row['review_id'],
            review_text=row['review_text'],
            similarity_score=row['similarity'],
            generated_response=generated_text if idx == 0 else None  # Include generated response only for the first result
        )
        for idx, row in enumerate(results)
    ]
    logger.info(f"Processed query for text: {request.query_text}")
    return response

if __name__ == '__main__':
    # Run the API server with Uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
