import requests

def search_pubmed(query: str, max_results: int = 5) -> str:
    """
    Mock implementation of a PubMed literature search tool.
    In a real scenario, this would use the NCBI E-utilities API.
    """
    # For demonstration purposes, returning mock data based on the query.
    mock_db = {
        "yeast": [
            "[PMID: 3456781] Genomic analysis of Saccharomyces cerevisiae stress response.",
            "[PMID: 3910293] Nitrogen metabolism during anaerobic fermentation.",
            "[PMID: 4102938] Engineered yeast strains for elevated thiol production."
        ],
        "crispr": [
            "[PMID: 3102938] Off-target effects in CRISPR-Cas9 genome editing.",
            "[PMID: 3829102] High-throughput CRISPR screening in mammalian cells."
        ]
    }
    
    query_lower = query.lower()
    results = []
    for key, articles in mock_db.items():
        if key in query_lower:
            results.extend(articles)
            
    if not results:
        return f"No literature found for query: '{query}'."
        
    return "\n".join(results[:max_results])

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
