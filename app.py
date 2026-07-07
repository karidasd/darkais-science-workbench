import streamlit as st
from src.orchestrator.coordinator import process_research_task
from src.compute.job_dispatcher import dispatch_folding_job

st.set_page_config(page_title="DarkAIs Science Workbench", layout="wide", page_icon="🧬")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600&family=Inter:wght@300;400&display=swap');
  .stApp { background-color: #0d1117; color: #c9d1d9; }
  h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; color: #58a6ff; }
  .stButton>button { background-color: #238636; color: white; border: none; font-weight: bold; }
  .stButton>button:hover { background-color: #2ea043; }
  .log-box { background-color: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 8px; font-family: monospace; color: #8b949e; }
  .artifact-box { background-color: #0d1117; border: 1px solid #58a6ff; padding: 20px; border-radius: 8px; box-shadow: 0 0 15px rgba(88, 166, 255, 0.2); }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🧬 DarkAIs Science Workbench</h1>", unsafe_allow_html=True)
st.markdown("*An Enterprise-Grade, Multi-Agent IDE for Biological Research.*")

# Sidebar for API keys and Compute settings
with st.sidebar:
    st.header("⚙️ Configuration (BYOK)")
    api_key = st.text_input("OpenAI / DeepSeek API Key", type="password")
    
    st.header("🖥️ Compute Backend")
    compute_node = st.selectbox("Execution Environment", ["Local Jupyter Kernel", "HPC Cluster (SSH)", "Modal Serverless GPU"])
    
    st.markdown("---")
    st.markdown("**Agents Online:**")
    st.markdown("- 🧠 Generalist Coordinator")
    st.markdown("- 👨‍🔬 Literature Specialist")
    st.markdown("- ⚖️ Critic / Reviewer")

tabs = st.tabs(["📚 Literature & Orchestration", "🖥️ Heavy Compute (BioNeMo Mock)"])

with tabs[0]:
    st.markdown("### Agentic Research Task")
    task_input = st.text_area("Describe your research request:", placeholder="e.g. Analyze recent literature on CRISPR off-target effects and summarize the main genetic causes.")
    
    if st.button("🚀 Execute Actor-Critic Pipeline"):
        if not api_key:
            st.error("API Key is required to run the agents.")
        elif not task_input:
            st.warning("Please enter a task.")
        else:
            with st.spinner("Orchestrating agents..."):
                result = process_research_task(api_key, task_input)
                
            st.markdown("### 📜 Execution Logs")
            log_html = "<br>".join(result["logs"])
            st.markdown(f"<div class='log-box'>{log_html}</div>", unsafe_allow_html=True)
            
            if result.get("final_artifact"):
                st.markdown("### 🧪 Generated Artifact")
                if result["approved"]:
                    st.success("✅ Passed Reviewer Agent Validation")
                else:
                    st.error(f"❌ Reviewer Agent Rejected: {result['feedback']}")
                    
                st.markdown(f"<div class='artifact-box'>{result['final_artifact']}</div>", unsafe_allow_html=True)

with tabs[1]:
    st.markdown("### Remote Protein Folding (Compute Dispatch)")
    st.markdown(f"*Current Environment: **{compute_node}***")
    
    seq_input = st.text_area("Protein FASTA Sequence:", placeholder=">Seq1\nMKALIVLGLVAA...")
    
    if st.button("⚡ Dispatch to Cluster"):
        with st.spinner(f"Submitting job to {compute_node}..."):
            job_res = dispatch_folding_job(seq_input)
            
        if job_res.get("status") == "completed":
            st.success(f"Job completed on {job_res['compute_backend']}")
            st.metric("pLDDT Confidence Score", f"{job_res['plddt_score']}%")
            st.code(job_res["structure_preview"], language="text")
        else:
            st.error(job_res.get("error", "Job failed."))
