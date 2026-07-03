"""
retriever_agent.py

Agent 2: RetrieverAgent  (the "R" in RAG)
Given the resume text and a job description, this agent chunks the job
description, embeds all chunks + the resume using TF-IDF vectors, and
retrieves the most relevant chunks via cosine similarity.

This is a lightweight, dependency-free form of RAG (no external vector DB
or API key needed) which is perfect for a local demo, while still being a
genuine retrieval step that augments what the SuggestionAgent generates.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.text_utils import chunk_text


class RetrieverAgent:
    name = "RetrieverAgent"

    def run(self, resume_clean_text: str, job_description: str, top_k: int = 3):
        chunks = chunk_text(job_description, chunk_size=60, overlap=10)
        if not chunks:
            return {"retrieved_chunks": [], "similarity_score": 0.0}

        documents = [resume_clean_text] + chunks
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(documents)

        resume_vector = tfidf_matrix[0:1]
        chunk_vectors = tfidf_matrix[1:]

        similarities = cosine_similarity(resume_vector, chunk_vectors)[0]

        ranked = sorted(
            zip(chunks, similarities), key=lambda x: x[1], reverse=True
        )
        top_chunks = ranked[:top_k]

        overall_similarity = float(similarities.mean()) if len(similarities) else 0.0

        return {
            "retrieved_chunks": [
                {"text": c, "relevance": round(float(s), 4)} for c, s in top_chunks
            ],
            "similarity_score": round(overall_similarity, 4)
        }
