import os
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# In-memory "Vector DB" using pure python lists
_documents = []
_metadatas = []
_vectorizer = None
_tfidf_matrix = None

def ingest_pdf(file_path: str, document_name: str) -> str:
    """
    Reads a PDF using pypdf, chunks it, and stores it in memory.
    Uses TF-IDF for lightweight, memory-efficient text vectorization.
    """
    global _vectorizer, _tfidf_matrix, _documents, _metadatas
    
    try:
        reader = PdfReader(file_path)
        chunks_added = 0
        
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if not text:
                continue
                
            # Simple chunking by double newlines (paragraphs)
            paragraphs = [p.strip() for p in text.split('\\n\\n') if len(p.strip()) > 50]
            
            # Fallback if no double newlines
            if not paragraphs:
                paragraphs = [text[i:i+500] for i in range(0, len(text), 500)]
                
            for para in paragraphs:
                _documents.append(para)
                _metadatas.append({"source": document_name, "page": page_num + 1})
                chunks_added += 1
                
        if chunks_added == 0:
            return f"No readable text found in {document_name}."
            
        # Re-fit the TF-IDF vectorizer on all documents
        _vectorizer = TfidfVectorizer(stop_words='english')
        _tfidf_matrix = _vectorizer.fit_transform(_documents)
        
        return f"Successfully ingested {chunks_added} chunks from {document_name}."
    except Exception as e:
        return f"Error ingesting PDF: {str(e)}"


def query_evidence_db(query: str, n_results: int = 3) -> str:
    """
    Searches the in-memory chunks using Cosine Similarity on TF-IDF vectors.
    """
    global _vectorizer, _tfidf_matrix, _documents, _metadatas
    
    if not _documents or _vectorizer is None:
        return "Evidence Database is currently empty. Please upload a PDF first."
        
    try:
        # Vectorize the query
        query_vec = _vectorizer.transform([query])
        
        # Compute cosine similarity
        similarities = cosine_similarity(query_vec, _tfidf_matrix).flatten()
        
        # Get top N indices
        top_indices = np.argsort(similarities)[-n_results:][::-1]
        
        # If the highest similarity is 0, no match
        if similarities[top_indices[0]] == 0:
            return "No relevant evidence found in the database."
            
        context_parts = []
        for idx in top_indices:
            if similarities[idx] > 0.05:  # Arbitrary threshold
                meta = _metadatas[idx]
                doc = _documents[idx]
                context_parts.append(f"[Source: {meta['source']}, Page: {meta['page']}]\\n{doc}")
                
        if not context_parts:
            return "No relevant evidence found."
            
        return "\\n\\n---\\n\\n".join(context_parts)
    except Exception as e:
        return f"Error querying database: {str(e)}"
