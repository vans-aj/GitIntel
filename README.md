# 🔍 GitHub RAG Code Analyzer

Chat with any GitHub file using AI. Chrome Extension + FastAPI backend.

## Setup

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt --timeout 120
cp .env.example .env        # add your OPENAI_API_KEY
uvicorn main:app --reload --port 8000
```

### Chrome Extension
```bash
cd chrome-extension
npm install
npm run build
```
Load `chrome-extension/dist/` as unpacked extension in `chrome://extensions/`

## Usage
1. Open any GitHub file (URL must have `/blob/`)
2. Click the extension icon
3. Click **Scan Current File**
4. Chat with the AI about the code
