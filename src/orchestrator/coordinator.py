import json
import time
from openai import OpenAI
from src.skills.bio_tools import search_pubmed
from src.skills.code_executor import execute_python_code
from src.orchestrator.actor_critic import run_actor_critic

def process_research_task(api_key: str, task: str, memory: list):
    """
    The Generalist Coordinator Agent with Tool Calling.
    Uses OpenAI function calling to intelligently invoke tools.
    """
    client = OpenAI(api_key=api_key)
    logs = []
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_pubmed",
                "description": "Searches PubMed for literature and returns abstracts.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "The search query (e.g. 'CRISPR Cas9')."},
                        "max_results": {"type": "integer", "description": "Number of results to fetch (default 3)."}
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "execute_python",
                "description": "Executes Python code in a safe REPL to analyze data.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "Valid Python code to execute."}
                    },
                    "required": ["code"]
                }
            }
        }
    ]

    messages = [{"role": "system", "content": "You are the Coordinator Agent. Use tools to gather data before summarizing. You must rely on the Critic to finalize."}]
    messages.extend(memory)
    messages.append({"role": "user", "content": task})
    
    logs.append("⚙️ Coordinator analyzing task and deciding tools...")
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    
    msg = response.choices[0].message
    context = ""
    
    if msg.tool_calls:
        for tool_call in msg.tool_calls:
            if tool_call.function.name == "search_pubmed":
                args = json.loads(tool_call.function.arguments)
                logs.append(f"🔍 Executing Literature Search for: {args['query']}")
                context += "LITERATURE:\\n" + search_pubmed(args['query'], args.get('max_results', 3)) + "\\n"
                logs.append("📚 Literature retrieved successfully.")
                
            elif tool_call.function.name == "execute_python":
                args = json.loads(tool_call.function.arguments)
                logs.append(f"🐍 Executing Python Code:\\n```python\\n{args['code']}\\n```")
                result = execute_python_code(args['code'])
                context += "CODE EXECUTION RESULT:\\n" + result + "\\n"
                logs.append(f"🖥️ Code execution returned output length: {len(result)}")
    else:
        logs.append("⚠️ No tools required. Proceeding with existing knowledge.")
        context = "Use internal knowledge."
        
    # Step 2: Actor-Critic Delegation
    logs.append("🧠 Delegating generation to Actor-Critic pair...")
    ac_result = run_actor_critic(api_key, task, context)
    
    if "error" in ac_result:
        logs.append(f"❌ Error during AI generation: {ac_result['error']}")
        return {"logs": logs, "final_artifact": None, "approved": False, "feedback": ""}
        
    logs.append(f"👨‍🔬 Actor generated a draft of length {len(ac_result['draft'])}.")
    
    if ac_result["approved"]:
        logs.append("✅ Critic Agent APPROVED the draft.")
    else:
        logs.append(f"❌ Critic Agent REJECTED the draft. Feedback: {ac_result['critic_feedback']}")
        
    return {
        "logs": logs,
        "final_artifact": ac_result["draft"],
        "approved": ac_result["approved"],
        "feedback": ac_result["critic_feedback"]
    }
