import streamlit as st
from stmol import showmol
import py3Dmol
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
  .log-box { background-color: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 8px; font-family: monospace; color: #8b949e; font-size: 0.85rem; margin-bottom: 10px; }
  .artifact-box { background-color: #0d1117; border: 1px solid #58a6ff; padding: 20px; border-radius: 8px; box-shadow: 0 0 15px rgba(88, 166, 255, 0.2); margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🧬 DarkAIs Science Workbench</h1>", unsafe_allow_html=True)
st.markdown("*An Enterprise-Grade, Multi-Agent IDE for Biological Research.*")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar for API keys and Compute settings
with st.sidebar:
    st.header("⚙️ Configuration (BYOK)")
    api_key = st.text_input("Groq API Key (Free)", type="password", help="Get a free key at https://console.groq.com/keys")
    st.markdown("[Get Free Groq Key](https://console.groq.com/keys)")
    
    st.header("🖥️ Compute Backend")
    compute_node = st.selectbox("Execution Environment", ["Local Sandbox", "HPC Cluster (SSH)", "Modal Serverless GPU"])
    
    st.markdown("---")
    st.markdown("**Agents Online:**")
    st.markdown("🟢 Generalist Coordinator")
    st.markdown("🟢 PubMed / Literature Specialist")
    st.markdown("🟢 Python Code Executor")
    st.markdown("🟢 Critic / Reviewer")
    
    if st.button("🗑️ Clear Session"):
        st.session_state.chat_history = []
        st.rerun()

tabs = st.tabs(["📚 Research Agent Chat", "🖥️ 3D Protein Rendering (BioNeMo Mock)"])

with tabs[0]:
    for msg in st.session_state.chat_history:
        with st.chat_message("user" if msg["role"] == "user" else "assistant"):
            st.markdown(msg["content"])
            
    if prompt := st.chat_input("Ask the AI Workbench to research something..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            if not api_key:
                st.error("API Key is required to run the agents.")
            else:
                with st.spinner("Agents are working..."):
                    # Pass the conversation history to the agent (last 4 messages for context)
                    memory = [{"role": m["role"], "content": m["content"]} for m in st.session_state.chat_history[-4:-1]]
                    
                    result = process_research_task(api_key, prompt, memory)
                    
                    st.markdown("##### 📜 Execution Logs (Coordinator & Tools)")
                    log_html = "<br>".join(result["logs"])
                    st.markdown(f"<div class='log-box'>{log_html}</div>", unsafe_allow_html=True)
                    
                    if result.get("final_artifact"):
                        if result["approved"]:
                            st.success("✅ Passed Reviewer Agent Validation")
                        else:
                            st.error(f"❌ Reviewer Agent Rejected: {result['feedback']}")
                            
                        st.markdown(f"<div class='artifact-box'>{result['final_artifact']}</div>", unsafe_allow_html=True)
                        st.session_state.chat_history.append({"role": "assistant", "content": result['final_artifact']})

with tabs[1]:
    st.markdown("### 3D Molecular Visualization")
    st.markdown("*Use py3Dmol to render a PDB code directly.*")
    
    c1, c2 = st.columns([1, 3])
    with c1:
        pdb_code = st.text_input("Enter PDB Code:", "1A2C")
        style = st.selectbox("Style", ["cartoon", "stick", "sphere", "surface"])
        color = st.selectbox("Color", ["spectrum", "chain", "secondary structure"])
        
        if st.button("⚡ Render Model"):
            pass # Triggers UI rerun
            
    with c2:
        try:
            view = py3Dmol.view(query=f'pdb:{pdb_code.lower()}', width=800, height=500)
            if style == "surface":
                view.addSurface(py3Dmol.VDW, {'opacity': 0.8})
            else:
                view.setStyle({style: {'color': color}})
            view.zoomTo()
            showmol(view, height=500, width=800)
        except Exception as e:
            st.error(f"Could not render molecule: {str(e)}")
