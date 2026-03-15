import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool
from duckduckgo_search import DDGS

@tool("Search Tool")
def search_tool(query: str) -> str:
    """Search the web for relevant information."""
    with DDGS() as ddgs:
        results = [r for r in ddgs.text(query, max_results=5)]
        return str(results)

load_dotenv()

llm_fast = LLM(model="gemini/gemini-2.5-flash", api_key=os.environ.get("GEMINI_API_KEY"))
llm_pro = LLM(model="gemini/gemini-2.5-pro", api_key=os.environ.get("GEMINI_API_KEY"))

# ──────────────────────────────────────────────────────────────────
# DATA LOADER
# Load whatever you want the crew to analyse.
# Examples below — uncomment what fits your use case.
# ──────────────────────────────────────────────────────────────────

def load_from_github(repo: str, path: str) -> str:
    """Read a file from any public or private GitHub repo."""
    token = os.environ.get("GITHUB_TOKEN")
    url = f"https://raw.githubusercontent.com/{repo}/main/{path}"
    headers = {"Authorization": f"token {token}"} if token else {}
    r = requests.get(url, headers=headers)
    return r.text[:15000]

def load_from_file(path: str) -> str:
    """Read a local file."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()[:15000]

def load_from_url(url: str) -> str:
    """Fetch raw text content from any URL."""
    r = requests.get(url)
    return r.text[:15000]

# ──────────────────────────────────────────────────────────────────
# EDIT THIS SECTION — point the crew at your data
# ──────────────────────────────────────────────────────────────────

context = """
Paste or load whatever you want audited here.

Examples:
  - load_from_github('username/repo', 'src/main.py')
  - load_from_file('my_document.txt')
  - load_from_url('https://example.com/data.json')
  - A raw string of text, a business plan, a dataset description, anything.
"""

# ──────────────────────────────────────────────────────────────────
# DISCORD NOTIFIER
# ──────────────────────────────────────────────────────────────────

def notify_discord(report_path: str):
    webhook = os.environ.get("DISCORD_WEBHOOK")
    if not webhook:
        print("No DISCORD_WEBHOOK set, skipping.")
        return
    requests.post(webhook, json={"content": f"## AI Audit — {datetime.now().strftime('%d %B %Y')}\nThe automated audit has completed. Full report attached below."})
    with open(report_path, "rb") as f:
        requests.post(webhook, files={"file": (report_path, f, "text/plain")})

# ──────────────────────────────────────────────────────────────────
# AGENTS
# Add, remove, or rename agents to fit your use case.
# Each agent is a specialist. Give them a clear role and backstory.
# ──────────────────────────────────────────────────────────────────

lead = Agent(
    role="Lead Analyst",
    goal="Give the final verdict and the top 3 actionable recommendations.",
    backstory="Senior expert with 15 years of experience. Direct, precise, no fluff.",
    llm=llm_pro,
    verbose=True
)

specialist = Agent(
    role="Domain Specialist",
    goal="Deeply analyse the subject matter and identify all issues and opportunities.",
    backstory="Expert in the relevant domain. You spot patterns, risks, and improvements instantly.",
    llm=llm_pro,
    tools=[search_tool],
    verbose=True
)

critic = Agent(
    role="Critical Reviewer",
    goal="Challenge every assumption. Find what is missing, broken, or risky.",
    backstory="Devil's advocate. You find the edge cases and failure modes everyone else misses.",
    llm=llm_fast,
    tools=[search_tool],
    verbose=True
)

strategist = Agent(
    role="Strategist",
    goal="Prioritize findings. Decide what must be acted on now vs later.",
    backstory="Ruthless prioritizer. You cut through noise and focus on what moves the needle.",
    llm=llm_pro,
    tools=[search_tool],
    verbose=True
)

# ──────────────────────────────────────────────────────────────────
# TASKS
# Each task maps to one agent. Context chains results between agents.
# ──────────────────────────────────────────────────────────────────

specialist_task = Task(
    description=f"Analyse the following in depth. Identify all issues, risks, and opportunities.\n\nINPUT:\n{context}",
    agent=specialist,
    expected_output="Detailed analysis with specific findings and evidence."
)

critic_task = Task(
    description="Challenge the specialist's findings. What did they miss? What are the worst-case scenarios?",
    agent=critic,
    expected_output="Critical review highlighting gaps, risks, and overlooked issues.",
    context=[specialist_task]
)

strategist_task = Task(
    description="Review all findings. Prioritize them. What must be acted on immediately vs what can wait?",
    agent=strategist,
    expected_output="Prioritized action plan with clear P0/P1/P2 classification.",
    context=[specialist_task, critic_task]
)

lead_task = Task(
    description="Review everything. Give the final verdict and the exact top 3 actions to take right now.",
    agent=lead,
    expected_output="Final verdict with top 3 immediate action items, each with clear rationale.",
    context=[strategist_task]
)

# ──────────────────────────────────────────────────────────────────
# CREW
# ──────────────────────────────────────────────────────────────────

crew = Crew(
    agents=[specialist, critic, strategist, lead],
    tasks=[specialist_task, critic_task, strategist_task, lead_task],
    verbose=True
)

if __name__ == "__main__":
    print("\nStarting audit...")
    result = crew.kickoff()

    report_path = f"audit_{datetime.now().strftime('%d-%m-%y_%H-%M')}.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(str(result))

    notify_discord(report_path)

    print(f"\nAudit complete. Report saved to: {report_path}")
    print(result)
