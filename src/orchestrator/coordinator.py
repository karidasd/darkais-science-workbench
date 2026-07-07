from src.skills.bio_tools import search_pubmed
from src.orchestrator.actor_critic import run_actor_critic
import time

def process_research_task(api_key: str, task: str):
    """
    The Generalist Coordinator Agent.
    1. Identifies the need for literature.
    2. Uses the PubMed skill.
    3. Triggers the Actor-Critic loop to generate the final artifact.
    """
    logs = []
    
    # Step 1: Tool execution
    logs.append("⚙️ Coordinator identifying tools needed: PubMed Search")
    time.sleep(0.5)
    
    # Extract naive keyword (Mock behavior for coordinator)
    keyword = "yeast" if "yeast" in task.lower() else "crispr" if "crispr" in task.lower() else "yeast"
    
    logs.append(f"🔍 Executing Literature Search for: {keyword}")
    context = search_pubmed(keyword)
    logs.append(f"📚 Retrieved {len(context.split('\\n'))} papers from literature.")
    
    # Step 2: Actor-Critic Delegation
    logs.append("🧠 Delegating generation to Actor-Critic pair...")
    ac_result = run_actor_critic(api_key, task, context)
    
    if "error" in ac_result:
        logs.append(f"❌ Error during AI generation: {ac_result['error']}")
        return {"logs": logs, "final_artifact": None, "approved": False}
        
    logs.append(f"👨‍🔬 Actor generated a draft of length {len(ac_result['draft'])}.")
    
    if ac_result["approved"]:
        logs.append("✅ Critic Agent APPROVED the draft. Citations are accurate.")
    else:
        logs.append(f"❌ Critic Agent REJECTED the draft. Feedback: {ac_result['critic_feedback']}")
        
    return {
        "logs": logs,
        "final_artifact": ac_result["draft"],
        "approved": ac_result["approved"],
        "feedback": ac_result["critic_feedback"]
    }
