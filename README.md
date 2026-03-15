# CrewAI Auditor Template

A plug-and-play AI crew that analyses **anything** — code, documents, business plans, datasets, APIs — and delivers a structured report to Discord or a local `.md` file.

Built with [CrewAI](https://github.com/crewAIInc/crewAI) and Google Gemini. Free to run on the Gemini API free tier.

---

## What It Does

- Loads any data source (GitHub repo, local file, URL, or raw text)
- Runs 4 specialized AI agents in sequence: Specialist → Critic → Strategist → Lead
- Each agent builds on the previous one's findings
- Saves a timestamped `.md` audit report locally
- Optionally uploads the full report to a Discord channel

---

## Quickstart

### 1. Clone & Install

```bash
git clone https://github.com/l3sm/crewai-auditor-template.git
cd crewai-auditor-template
python3 -m venv crewai-env
source crewai-env/bin/activate
pip install crewai crewai-tools duckduckgo-search python-dotenv requests
```

### 2. Configure Keys

```bash
cp .env.example .env
nano .env
```

| Key | Where to get it | Required? |
|---|---|---|
| `GEMINI_API_KEY` | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) — free | ✅ Yes |
| `GITHUB_TOKEN` | GitHub → Settings → Developer Settings → Tokens | Only for private repos |
| `DISCORD_WEBHOOK` | Discord → Channel → Integrations → Webhooks | Only for Discord reports |

### 3. Point It at Your Data

Open `crew_template.py` and edit the `context` section:

```python
# Load from a GitHub repo
context = load_from_github('username/repo', 'path/to/file.py')

# Load from a local file
context = load_from_file('my_business_plan.txt')

# Load from a URL
context = load_from_url('https://api.example.com/data.json')

# Or just paste raw text directly
context = """
Your business plan, essay, codebase, dataset description,
or anything else you want the crew to analyse.
"""
```

### 4. Run

```bash
python crew_template.py
```

The report is saved as `audit_DD-MM-YY_HH-MM.md` and uploaded to Discord if configured.

---

## The Agents

| Agent | Model | Role |
|---|---|---|
| Lead Analyst | Gemini 2.5 Pro | Final verdict & top 3 actions |
| Strategist | Gemini 2.5 Pro | Prioritization (P0/P1/P2) |
| Domain Specialist | Gemini 2.5 Pro | Deep analysis |
| Critical Reviewer | Gemini 2.5 Flash | Devil's advocate, edge cases |

---

## Customization

**Swap the model** — replace `gemini/gemini-2.5-pro` with any [LiteLLM-supported model](https://docs.litellm.ai/docs/providers):
```python
llm_pro = LLM(model="openai/gpt-4o", api_key=os.environ.get("OPENAI_API_KEY"))
llm_fast = LLM(model="ollama/llama3.1", base_url="http://localhost:11434")
```

**Add agents** — copy any `Agent` + `Task` block and give it a new role.

**Change the output** — modify `notify_discord()` to send to Slack, email, or save to Notion instead.

---

## Use Case Examples

| What to audit | How to load it |
|---|---|
| GitHub codebase | `load_from_github('user/repo', 'src/main.py')` |
| Business plan (txt/md) | `load_from_file('plan.txt')` |
| API response / JSON data | `load_from_url('https://...')` |
| Essay or document | Paste directly into `context` |
| Resume | `load_from_file('resume.txt')` |
| Competitor website copy | `load_from_url('https://competitor.com')` |

---

## Shell Alias (Optional)

Run the crew from anywhere with one word:

```bash
echo 'alias audit="cd ~/crewai-auditor-template && source crewai-env/bin/activate && python crew_template.py"' >> ~/.bashrc
source ~/.bashrc
```

Then just type `audit` in your terminal.

---

## Requirements

- Python 3.10+
- Free [Google AI Studio](https://aistudio.google.com) account for the API key
