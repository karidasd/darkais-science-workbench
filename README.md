# 🧬 DarkAIs Science Workbench

An open-source, Multi-Agent IDE for Biological Research, inspired by Anthropic's Claude Science. 

This repository demonstrates advanced Agentic AI architectures including **Actor-Critic Validation**, **Tool Calling (MCPs)**, and **Compute Delegation**.

## 🧠 Architecture Overview

### 1. Actor-Critic Multi-Agent Orchestration
Instead of relying on a single LLM to generate answers, this workbench utilizes a multi-agent approach:
- **Actor Agent**: Generates scientific drafts and analyzes data based on biological contexts.
- **Critic (Reviewer) Agent**: Acts as an automated peer-reviewer. It strictly validates the Actor's output, checking for hallucinated citations, biological accuracy, and logical consistency before presenting it to the user.

### 2. Tool Integration (`src/skills`)
Agents are equipped with real-world bioinformatics tools. For example, the `bio_tools.py` module allows the Coordinator Agent to query literature databases (like PubMed) dynamically and parse FASTA sequences.

### 3. Compute Dispatcher (`src/compute`)
Biological computations (like AlphaFold protein folding or genomic alignments) require massive compute. The `job_dispatcher.py` simulates dispatching heavy workloads to HPC Clusters over SSH or Serverless GPUs (e.g., Modal) without blocking the main agentic loop.

### 4. BYOK (Bring Your Own Key) Security & 100% Free Models
Designed for enterprise and academic deployment, the frontend does not hardcode API keys. Users inject their own **Groq API Keys (Free)** per session. This allows the Workbench to run entirely on open-source frontier models (like **Meta LLaMA 3 70B**) with zero inference costs and absolute data privacy.

### 5. 3D Molecule Visualization (`app.py`)
Integrated native support for rendering 3D protein structures (via PDB codes) using `py3Dmol`, allowing researchers to visually inspect computational biology results directly in the IDE.

---

## 🚀 Quick Start

1. Clone the repository:
```bash
git clone https://github.com/karidasd/darkais-science-workbench
cd darkais-science-workbench
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the Streamlit Application:
```bash
streamlit run app.py
```

## 🛠 Tech Stack
- **Frontend**: Streamlit
- **AI Backend**: OpenAI Python SDK with **Groq API** (running **LLaMA 3 70B**)
- **Data Parsing**: Biopython, Pandas, py3Dmol

---
*Developed by DarkAIs. Redefining scientific workflows through AI.*
