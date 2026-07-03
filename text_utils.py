"""
text_utils.py
Small helper functions used across agents: text cleaning, PDF extraction,
and a lightweight skill-keyword list used for overlap based scoring.
"""

import re
import io

# A reasonably broad list of common tech/skill keywords used for
# quick keyword-overlap analysis (used by ScorerAgent as a fallback
# signal alongside TF-IDF similarity).
COMMON_SKILLS = [
    "python", "java", "javascript", "typescript", "c++", "c#", "sql", "nosql",
    "flask", "django", "fastapi", "react", "angular", "vue", "node", "express",
    "html", "css", "git", "github", "docker", "kubernetes", "aws", "azure", "gcp",
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras",
    "machine learning", "deep learning", "nlp", "computer vision", "llm",
    "rag", "vector database", "embeddings", "prompt engineering", "agentic ai",
    "power bi", "tableau", "excel", "statistics", "data analysis",
    "rest api", "microservices", "system design", "testing", "ci/cd", "linux"
]


def clean_text(text: str) -> str:
    """Lowercase, strip extra whitespace, remove unusual characters."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\+\#\.\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract raw text from a PDF file's bytes using pypdf."""
    try:
        from pypdf import PdfReader
    except ImportError:
        from PyPDF2 import PdfReader  # fallback for older installs

    reader = PdfReader(io.BytesIO(file_bytes))
    text_parts = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        text_parts.append(page_text)
    return "\n".join(text_parts)


def find_matched_skills(text: str):
    """Return the subset of COMMON_SKILLS found in the given text."""
    cleaned = clean_text(text)
    found = [skill for skill in COMMON_SKILLS if skill in cleaned]
    return found


def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50):
    """Split text into overlapping word chunks for retrieval."""
    words = text.split()
    if not words:
        return []
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        start += chunk_size - overlap
    return chunks
