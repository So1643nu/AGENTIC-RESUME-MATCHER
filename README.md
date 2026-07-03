# Agentic Resume / Job Matcher (RAG + Multi-Agent, No API Key Required)

A local, agentic AI mini project that compares a resume against a job description
using a **4-agent pipeline** orchestrated by a central `Orchestrator`, with a
lightweight **RAG (Retrieval-Augmented Generation)** step and an **optional local
LLM (Ollama)** — no paid API key needed anywhere.

---

## 🧠 How it's "Agentic AI"

Instead of one script doing everything, the work is split across independent
agents, each with one responsibility. The **Orchestrator** decides the order,
passes data between them, and keeps the app alive even if one step fails.

```
User Input (Resume + Job Description)
        │
        ▼
 ┌───────────────┐
 │ 1. ParserAgent │  → cleans resume text (PDF or plain text)
 └───────┬───────┘
         ▼
 ┌────────────────────┐
 │ 2. RetrieverAgent   │  → RAG step: TF-IDF retrieval of the most
 │   (RAG - Retrieval) │     relevant job-description chunks vs resume
 └───────┬────────────┘
         ▼
 ┌───────────────┐
 │ 3. ScorerAgent │  → blends similarity + keyword overlap into a
 └───────┬───────┘     0-100 fit score, matched/missing skills
         ▼
 ┌─────────────────────┐
 │ 4. SuggestionAgent   │  → RAG - Generation step: local LLM (Ollama)
 │  (RAG - Generation)  │     if available, else rule-based fallback
 └───────┬─────────────┘
         ▼
   JSON result → Flask API → Frontend
```

This qualifies as **Agentic AI** because agents act autonomously in sequence,
each making decisions (e.g., the SuggestionAgent decides whether to call an
LLM or fall back), and **RAG** because job-description context is *retrieved*
before being used to *generate* suggestions.

---

## 📁 Project Structure

```
agentic_resume_matcher/
├── backend/
│   ├── app.py                  # Flask app (routes)
│   ├── orchestrator.py         # Runs the agent pipeline
│   ├── agents/
│   │   ├── parser_agent.py
│   │   ├── retriever_agent.py  # RAG retrieval (TF-IDF)
│   │   ├── scorer_agent.py
│   │   └── suggestion_agent.py # RAG generation (LLM + fallback)
│   ├── utils/
│   │   ├── llm_client.py       # Ollama wrapper (local, no API key)
│   │   └── text_utils.py
│   ├── uploads/                # Temp folder (gitignored)
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── data/
│   └── sample_job_descriptions.json
├── .gitignore
└── README.md
```

---

## ⚙️ Requirements

- Python 3.9+
- VS Code with the **Python extension** installed
- (Optional, for real AI-generated suggestions) [Ollama](https://ollama.com) — free, runs locally, no API key

---

## 🚀 Setup & Run in VS Code (step-by-step)

### 1. Unzip and open the project
- Unzip `agentic_resume_matcher.zip`
- Open VS Code → `File > Open Folder` → select the unzipped `agentic_resume_matcher` folder

### 2. Open a terminal in VS Code
`Terminal > New Terminal`

### 3. Create and activate a virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```
You should see `(venv)` appear in your terminal prompt.

### 4. Install dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 5. (Optional but recommended) Set up Ollama for real LLM suggestions
If you skip this step, the app **still works fully** — it just uses rule-based
suggestions instead of LLM-generated ones.

```bash
# 1. Download & install Ollama from https://ollama.com (Windows/Mac/Linux installer)
# 2. After installing, pull a small free local model:
ollama pull llama3.2
# 3. Ollama automatically runs a local server at http://localhost:11434
#    Leave it running in the background — no API key, no internet calls, no cost.
```

### 6. Run the Flask app
From inside the `backend` folder:
```bash
python app.py
```
You should see output like:
```
 * Running on http://127.0.0.1:5000
```

### 7. Open the website
In your browser, go to:
```
http://localhost:5000
```
This is your **website link** — the Flask app itself serves the frontend, so
there's nothing extra to configure.

### 8. Use the app
1. Pick a sample job description (or paste your own)
2. Upload a resume (`.pdf` / `.txt`) or paste resume text
3. Click **"Run Agent Pipeline"**
4. See the fit score, matched/missing skills, and suggestions
5. Expand **"Agent Trace"** to show each agent's execution status — great for
   demoing the "agentic" part during evaluation

---

## 🧪 Quick sanity test (no UI)

```bash
curl -X POST http://localhost:5000/api/analyze \
  -F "job_description=We need a Python developer with Flask and REST API experience" \
  -F "resume_text=I have 2 years experience in Python, Flask, Git and SQL"
```

---

## 📤 Push to GitHub from VS Code

### 1. Initialize git (if not already)
```bash
cd ..   # back to agentic_resume_matcher root
git init
git add .
git commit -m "Initial commit: Agentic Resume Matcher with RAG pipeline"
```

### 2. Create a new repo on GitHub
- Go to github.com → New Repository → name it e.g. `agentic-resume-matcher`
- Do **not** initialize with a README (you already have one)

### 3. Link and push
```bash
git branch -M main
git remote add origin https://github.com/<your-username>/agentic-resume-matcher.git
git push -u origin main
```

### 4. (Alternative) Use VS Code's built-in Git UI
- Click the **Source Control** icon (left sidebar)
- Click **Initialize Repository**
- Stage all changes (+), write a commit message, click **Commit**
- Click **Publish Branch** and follow the GitHub sign-in prompt

---

## 🎤 How to explain this in your viva (talking points)

- **"Why is this agentic?"** → Each step (parse, retrieve, score, suggest) is
  an independent agent object with a single job. The `Orchestrator` chains
  them and handles failures — that's agent orchestration.
- **"Where's the RAG?"** → `RetrieverAgent` retrieves the most relevant chunks
  of the job description based on similarity to the resume (Retrieval), and
  `SuggestionAgent` uses that retrieved context to generate suggestions
  (Generation) — classic RAG pattern, implemented locally with TF-IDF instead
  of a paid embeddings API.
- **"Why no API key?"** → Retrieval uses scikit-learn's TF-IDF (fully local,
  free). Generation optionally uses Ollama, a free local LLM runtime. If
  Ollama isn't running, the app automatically falls back to rule-based
  suggestions — so it never crashes and needs zero paid services.
- **"What would you improve with more time?"** → Swap TF-IDF for real sentence
  embeddings (e.g. `sentence-transformers`) and a vector DB (e.g. Chroma) for
  more semantic retrieval; add authentication; support multiple resumes at
  once (batch matching).

---

## 🛠️ Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: flask` | Make sure venv is activated, then re-run `pip install -r requirements.txt` |
| Port 5000 already in use | Change the port in `app.py`'s last line, e.g. `port=5050` |
| PDF text extraction returns empty | Try a text-based PDF (not a scanned image); or use the "Paste Text" tab instead |
| Suggestions always say "rule-based (fallback)" | Ollama isn't running — check with `ollama list` in a terminal, or ignore it, the app still works fully |
