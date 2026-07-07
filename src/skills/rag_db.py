import os
import fitz  # PyMuPDF
import chromadb
from sentence_transformers import SentenceTransformer

# Initialize ChromaDB client in memory for this session
_chroma_client = chromadb.Client()

# Create or get the collection
_collection = _chroma_client.get_or_create_collection(name="evidence_state")

# Initialize embedding model (runs locally)
# Using a lightweight model to ensure fast performance and no API costs
_embedder = SentenceTransformer("all-MiniLM-L6-v2")

def ingest_pdf(file_path: str, document_name: str) -> str:
    """
    Reads a PDF, chunks it into paragraphs, embeds them, and stores in ChromaDB.
    """
    try:
        doc = fitz.open(file_path)
        chunks = []
        metadatas = []
        ids = []
        
        chunk_idx = 0
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text("text")
            
            # Simple chunking by double newlines (paragraphs)
            paragraphs = [p.strip() for p in text.split('\\n\\n') if len(p.strip()) > 50]
            
            for para in paragraphs:
                chunks.append(para)
                metadatas.append({"source": document_name, "page": page_num + 1})
                ids.append(f"{document_name}_p{page_num}_{chunk_idx}")
                chunk_idx += 1
                
        if not chunks:
            return f"No readable text found in {document_name}."
            
        # Generate embeddings
        embeddings = _embedder.encode(chunks).tolist()
        
        # Store in ChromaDB
        _collection.add(
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )
        
        return f"Successfully ingested {len(chunks)} chunks from {document_name}."
    except Exception as e:
        return f"Error ingesting PDF: {str(e)}"


def query_evidence_db(query: str, n_results: int = 3) -> str:
    """
    Searches the ChromaDB for relevant context based on the query.
    """
    if _collection.count() == 0:
        return "Evidence Database is currently empty. Please upload a PDF first."
        
    try:
        query_embedding = _embedder.encode([query]).tolist()
        
        results = _collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        
        if not results['documents'][0]:
            return "No relevant evidence found in the database."
            
        context_parts = []
        for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
            context_parts.append(f"[Source: {meta['source']}, Page: {meta['page']}]\\n{doc}")
            
        return "\\n\\n---\\n\\n".join(context_parts)
    except Exception as e:
        return f"Error querying database: {str(e)}"
