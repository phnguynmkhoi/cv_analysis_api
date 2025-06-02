from google import genai
from dotenv import load_dotenv
import numpy as np
import os
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
import uuid
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

class Embedder:
    """
    Uses Gemini via LangChain to embed CV text for similarity search.
    """
    def __init__(self, google_api_key: 
                 str, qdrant_host: str = "localhost", qdrant_port: int = 6333):
        self.client = genai.Client(api_key=google_api_key)
        self.model = "gemini-embedding-exp-03-07"
        self.qdrant_client = QdrantClient(host=qdrant_host, port=qdrant_port)

        # Ensure qdrant collection exists
        self.collection_name = "cv_embeddings"
        if not self.qdrant_client.collection_exists(self.collection_name):
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=3072,
                    distance=Distance.COSINE
                )
            )
        
    def embed(self, text: str) -> list:
        """
        Embed the provided text using Gemini embedding model.

        Parameters:
            text (str): The text to embed.

        Returns:
            list: The embedding vector.
        """
        try:
            response = self.client.models.embed_content(
                model=self.model,
                contents=[text]
            )
        except Exception as e:
            raise Exception(f"Error embedding text: {str(e)}")
        
        return response.embeddings[0].values
    
    def embed_batch(self, texts: list) -> list:
        """
        Embed a batch of texts using Gemini embedding model.
        Parameters:
            texts (list): A list of texts to embed.
        Returns:
            list: A list of embedding vectors.
        """
        try:
            response = self.client.models.embed_content(
                model=self.model,
                contents=texts
            )
        except Exception as e:
            raise Exception(f"Error embedding batch: {str(e)}")
        
        return [embedding.values for embedding in response.embeddings]
    
    def embed_cv(self, person_id: str, resume_id: str, payload: dict):
        """
        Embed CV text and store it in the Qdrant collection.

        Parameters:
            payload (dict): The CV data containing 'skills', 'description', etc.
            person_id (str): Unique identifier for the person.
            resume_id (str): Unique identifier for the resume.

        Returns:
            PointStruct: The point struct containing the embedded vector and payload.
        """
        if not person_id or not resume_id:
            raise ValueError("Both person_id and resume_id must be provided.")

        skills = payload.get("skills", [])
        yoe = payload.get("years_of_experience", 0)
        skills_description = payload.get("skills_description", "")
        work_description = payload.get("work_description", "")
        full_description = f"{skills_description} {work_description}".strip()
        full_description_embedding = self.embed(full_description)

        point = PointStruct(
            id=int(resume_id),  # Generate a unique ID for the point
            vector=full_description_embedding,
            payload={
                "skills": skills,
                "years_of_experience": yoe,
                "person_id": person_id
            }
        )
        self.qdrant_client.upsert(
            collection_name=self.collection_name,
            points=[point]
        )
    
    def search(self, query: str, limit: int = 3):
        """
        Search for similar embeddings in the Qdrant collection.

        Parameters:
            query (str): The query text to search for.
            limit (int): The maximum number of results to return.

        Returns:
            list: List of matching points with their payloads.
        """
        query_embedding = self.embed(query)
        results = self.qdrant_client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            limit=limit
        )
        
        return results.points
        
    def search_with_filter(self, query: str, filter: dict, limit: int = 3):
        """
        Search for similar embeddings in the Qdrant collection with a filter.

        Parameters:
            query (str): The query text to search for.
            filter (dict): The filter to apply on the search.
            limit (int): The maximum number of results to return.

        Returns:
            list: List of matching points with their payloads.
        """
        skills = filter.get("skills", [])
        yoe = filter.get("yoe", 0)
        if skills is None and yoe is None:
            return self.search(query, limit)
        query_embedding = self.embed(query)
        results = self.qdrant_client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            query_filter={
                "must": [
                    {
                        "key": "years_of_experience",
                        "range": {
                            "gte": yoe
                        }
                    }
                ],
                "should": [
                    {"key": "skills", "match": {"value": skill}} for skill in skills
                ]
            },
            limit=limit
        )


        return results.points

if __name__ == "__main__":
    # Example usage
    embedder = Embedder(GOOGLE_API_KEY)
    # payload = {
    #     "skills": ["python", "data analysis"],
    #     "years_of_experience": 5,
    #     "skills_description": "Experienced in Python and data analysis.",
    #     "work_description": "Worked as a data analyst for 5 years."
    # }
    # person_id = "12345"
    # resume_id = "67890"
    # embedder.embed_cv(person_id, resume_id, payload)

    # payload = {
    #     "skills": ["python", "machine learning"],
    #     "years_of_experience": 3,
    #     "skills_description": "Skilled in Python and machine learning.",
    #     "work_description": "Worked as a machine learning engineer for 3 years."
    # }
    # embedder.embed_cv("54321", "09876", payload)

    # #payload for DE
    # payload = {
    #     "skills": ["python", "data engineering"],
    #     "years_of_experience": 4,
    #     "skills_description": "Experienced in Python and data engineering.",
    #     "work_description": "Worked as a data engineer for 4 years."
    # }
    # embedder.embed_cv("11223", "44556", payload)

    # # payload for PM
    # payload = {
    #     "skills": ["project management", "agile"],
    #     "years_of_experience": 6,
    #     "skills_description": "Experienced in project management and agile methodologies.",
    #     "work_description": "Worked as a project manager for 6 years."
    # }
    # embedder.embed_cv("77889", "99001", payload)

    #payload for SE
    # payload = {
    #     "skills": ["java", "software engineering"],
    #     "years_of_experience": 7,
    #     "skills_description": "Skilled in Java and software engineering.",
    #     "work_description": "Worked as a software engineer for 7 years."
    # }
    # embedder.embed_cv("22334", "55667", payload)

    # Search for similar CVs
    query = "Looking for an software engineer with experience in Python image processing"
    filter = {
    }
    results = embedder.search_with_filter(query, limit=5, filter=filter)
    print("Search Results:")
    # print(results)
    for result in results:
        print(f"{result}")
        print("---------------------")

