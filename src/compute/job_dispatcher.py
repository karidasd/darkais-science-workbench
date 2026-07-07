import time
import random

def dispatch_folding_job(protein_sequence: str) -> dict:
    """
    Simulates sending a heavy BioNeMo/AlphaFold job to a remote cluster.
    """
    if not protein_sequence:
        return {"status": "failed", "error": "No sequence provided."}
        
    # Simulate network latency and compute time
    time.sleep(2)
    
    # Mock result
    confidence_score = round(random.uniform(70.0, 98.0), 2)
    
    return {
        "status": "completed",
        "compute_backend": "Modal Serverless GPU (A100)",
        "plddt_score": confidence_score,
        "structure_preview": f"Helix(1-20), Sheet(25-40). Confidence: {confidence_score}%"
    }
