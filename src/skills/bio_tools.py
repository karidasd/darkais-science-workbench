from Bio import Entrez
import json

def search_pubmed(query: str, max_results: int = 5, email: str = "your.email@example.com") -> str:
    """
    Fetches actual literature from PubMed using Biopython's Entrez module.
    """
    Entrez.email = email
    
    try:
        # Search PubMed
        handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
        record = Entrez.read(handle)
        handle.close()
        
        id_list = record["IdList"]
        if not id_list:
            return f"No literature found for query: '{query}'."
            
        # Fetch details for the IDs
        handle = Entrez.efetch(db="pubmed", id=id_list, retmode="xml")
        papers = Entrez.read(handle)
        handle.close()
        
        results = []
        for paper in papers['PubmedArticle']:
            pmid = paper['MedlineCitation']['PMID']
            article = paper['MedlineCitation']['Article']
            title = article.get('ArticleTitle', 'No title available')
            
            abstract_text = "No abstract available."
            if 'Abstract' in article and 'AbstractText' in article['Abstract']:
                abstract_text = " ".join([str(text) for text in article['Abstract']['AbstractText']])
            
            results.append(f"[PMID: {pmid}] {title}\\nAbstract: {abstract_text}")
            
        return "\\n\\n".join(results)
        
    except Exception as e:
        return f"Error fetching from PubMed: {str(e)}"

def parse_fasta(sequence_data: str) -> dict:
    """
    Parses raw FASTA format into a structured dictionary.
    """
    lines = sequence_data.strip().split('\\n')
    parsed = {}
    current_header = None
    
    for line in lines:
        if line.startswith('>'):
            current_header = line[1:]
            parsed[current_header] = ""
        elif current_header:
            parsed[current_header] += line.strip()
            
    return parsed
