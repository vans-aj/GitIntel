# GitIntel 🔍

> Chat with any GitHub file using AI. Open a file on GitHub, ask questions, get instant answers.

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?style=flat-square)
![LangChain](https://img.shields.io/badge/LangChain-0.3-orange?style=flat-square)
![React](https://img.shields.io/badge/React-18-61dafb?style=flat-square)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-purple?style=flat-square)

---

## What is this?

GitIntel is a Chrome Extension + AI backend that lets you have a conversation with any code file on GitHub.

Open any file → Click the extension → Ask anything about the code.

```
You:  "What does this file do?"
AI:   "This is a FastAPI application that handles user authentication.
       It has 3 endpoints: /login, /register, and /logout..."

You:  "Are there any bugs?"
AI:   "Line 47 — the password is compared without hashing which is a
       security risk. Consider using bcrypt..."
```

---

## How it works

```
GitHub File
    ↓
Chrome Extension reads the code
    ↓
Sends to FastAPI backend
    ↓
LangChain splits code into chunks
    ↓
OpenAI converts chunks to vectors
    ↓
FAISS stores vectors in memory
    ↓
Your question finds the most relevant chunks
    ↓
GPT-4o-mini reads chunks + answers your question
```

This pattern is called **RAG** (Retrieval-Augmented Generation).

---

## Tech Stack

| Part | Technology |
|---|---|
| Chrome Extension | React 18 + Vite |
| Backend API | Python + FastAPI |
| AI Pipeline | LangChain + FAISS |
| LLM | OpenAI GPT-4o-mini |
| Embeddings | OpenAI text-embedding-3-small |

---

## Setup

You need:
- Python 3.11+
- Node.js 18+
- An OpenAI API key → [get one here](https://platform.openai.com/api-keys)

---

### 1. Clone the repo

```bash
git clone https://github.com/vans-aj/GitIntel.git
cd GitIntel
```

---

### 2. Backend setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate       # Mac/Linux
# venv\Scripts\activate        # Windows

# Install dependencies
pip install -r requirements.txt

# Add your API key
cp .env.example .env
# Open .env and add your OPENAI_API_KEY
```

Start the backend:
```bash
uvicorn main:app --reload --port 8000
```

You should see:
```
🚀 GitIntel starting...
INFO: Uvicorn running on http://127.0.0.1:8000
```

---

### 3. Chrome Extension setup

Open a new terminal:

```bash
cd chrome-extension
npm install
npm run build
```

Load in Chrome:
1. Go to `chrome://extensions/`
2. Turn on **Developer Mode** (top right)
3. Click **Load unpacked**
4. Select the `chrome-extension/dist/` folder

---

### 4. Use it

1. Make sure backend is running on port 8000
2. Open any GitHub file, for example:
   ```
   https://github.com/github/gitignore/blob/main/Python.gitignore
   ```
3. Click the **GitIntel** icon in Chrome toolbar
4. Click **Scan Current File**
5. Ask anything!

---

## Project Structure

```
GitIntel/
├── backend/
│   ├── main.py                    # FastAPI app entry point
│   ├── requirements.txt
│   ├── .env.example               # Copy this to .env
│   └── app/
│       ├── api/routes.py          # API endpoints
│       ├── core/config.py         # Settings from .env
│       ├── models/schemas.py      # Request/response types
│       ├── services/rag_service.py # RAG pipeline (main logic)
│       └── utils/code_utils.py    # Helper functions
│
└── chrome-extension/
    ├── public/
    │   ├── manifest.json          # Chrome extension config
    │   └── icons/
    └── src/
        ├── content.js             # Reads code from GitHub DOM
        ├── background.js          # Extension service worker
        ├── App.jsx                # Main UI
        ├── components/            # Header, Chat, Summary UI
        ├── hooks/                 # useChat, useGitHubCode
        ├── services/              # API calls to backend
        └── styles/                # CSS modules
```

---

## API Endpoints

| Method | Endpoint | What it does |
|---|---|---|
| GET | `/api/health` | Check if backend is running |
| POST | `/api/analyze` | Generate AI summary of code file |
| POST | `/api/chat` | Ask a question about the code |

Interactive docs available at: `http://localhost:8000/docs`

---

## Environment Variables

Create `backend/.env` from the example:

```env
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
CHUNK_SIZE=500
CHUNK_OVERLAP=50
MAX_TOKENS=2000
```

---

## Common Issues

**Extension says "Could not extract code"**
→ Make sure the URL has `/blob/` in it (you must be on a file page, not a folder)

**Backend offline warning in extension**
→ Run `uvicorn main:app --reload --port 8000` in the backend folder

**pip install times out**
→ Run `pip install -r requirements.txt --timeout 120`

**Chrome shows manifest error**
→ Make sure you selected `dist/` folder, not `chrome-extension/` folder

---

## Author

**Vansaj Rawat**

Built as a portfolio project to demonstrate RAG pipelines, LangChain, FastAPI, and Chrome Extension development.

---

> ⭐ Star this repo if you found it useful!
