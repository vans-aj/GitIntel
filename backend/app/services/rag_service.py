"""
RAG Service — GitHub Code Analyzer

Smart context-aware conversations:
- Casual messages (thanks, hi, ok) → instant friendly reply, no API cost
- Code questions → full RAG pipeline with FAISS + OpenAI
"""

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.schema import HumanMessage, AIMessage
from langchain.prompts import PromptTemplate
from app.core.config import get_settings
from app.utils.code_utils import truncate_code
import logging

logger = logging.getLogger(__name__)

# ── Casual intent detection ───────────────────────────────────────────────────

CASUAL_MAP = {
    "thank": "You're welcome! Feel free to ask anything else about the code. 😊",
    "thanks": "Happy to help! Any other questions about the code?",
    "thanku": "You're welcome! Let me know if you need anything else. 😊",
    "thank you": "Glad I could help! Ask me anything else about the code.",
    "thx": "No problem! What else would you like to know?",
    "ty": "You're welcome! 😊",
    "great": "Glad that helped! What else would you like to explore?",
    "awesome": "Thanks! Feel free to ask more questions. 🚀",
    "nice": "Thanks! Let me know if you want to dig deeper.",
    "cool": "Right? Let me know if you have more questions! 😄",
    "good": "Great! Is there anything else you'd like to know about this file?",
    "perfect": "Glad it's clear! Any other questions?",
    "excellent": "Thanks! Feel free to keep exploring.",
    "wow": "Ask me anything else about the code. 😄",
    "amazing": "Thanks! There's more to explore — just ask!",
    "ok": "Got it! Let me know if you have more questions.",
    "okay": "Sure thing! Any other questions?",
    "got it": "Great! Ask away if you have more questions.",
    "understood": "Perfect! What else would you like to know?",
    "sure": "Of course! What else would you like to explore?",
    "alright": "Sounds good! Any other questions?",
    "hi": "Hi there! 👋 I've analyzed the code file. What would you like to know?",
    "hello": "Hello! 👋 Ask me anything about the code.",
    "hey": "Hey! 👋 Ready to answer your code questions.",
    "bye": "Goodbye! Come back anytime. 👋",
    "goodbye": "See you! Happy coding! 👋",
    "yes": "Sure! What would you like to know?",
    "no": "No problem! Let me know if you need anything.",
    "yeah": "Sure! What would you like to know?",
    "yep": "Great! What else can I help with?",
    "help": "I can help you with:\n- **What does this file do?**\n- **Explain a specific function**\n- **Find potential bugs**\n- **Suggest improvements**\n- **List dependencies**\n\nJust ask!",
    "who are you": "I'm CodeRAG, an AI assistant that has read and indexed this code file. Ask me anything about it! 🤖",
    "what can you do": "I can:\n- 📖 Explain what the code does\n- 🐛 Find potential bugs\n- 💡 Suggest improvements\n- 🔍 Explain functions or classes\n- 📦 List dependencies\n- 🧪 Help write tests\n\nJust ask!",
}

def detect_casual(message: str):
    """Returns a canned response for casual messages, or None for code questions."""
    cleaned = message.strip().lower().rstrip("!.,?")
    # Exact match
    if cleaned in CASUAL_MAP:
        return CASUAL_MAP[cleaned]
    # Short message partial match (5 words or fewer)
    if len(cleaned.split()) <= 5:
        for trigger, response in CASUAL_MAP.items():
            if trigger in cleaned:
                return response
    return None


# ── Prompts ───────────────────────────────────────────────────────────────────

CODE_QA_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""You are CodeRAG, a friendly and expert software engineer assistant.

You are answering questions about a specific code file. Use the relevant code chunks below.

Guidelines:
- Be conversational yet precise
- Use markdown code blocks (```language) for any code examples
- Reference specific function, class, or variable names from the code
- If you spot bugs or improvements, proactively mention them
- Keep answers focused — not too long, not too short
- IMPORTANT: If the message is casual (hi, thanks, ok, great) — respond naturally and briefly. Do NOT force a code analysis for casual messages.

Relevant Code:
{context}

Question: {question}

Answer:""",
)

SUMMARY_PROMPT = """You are CodeRAG, an expert software engineer. Analyze this {language} file: '{filename}'.

Write a concise structured summary with these exact sections:
1. **Purpose**: What this file does (1-2 sentences)
2. **Key Components**: The most important classes, functions, or exports
3. **Dependencies**: External libraries/modules used
4. **Complexity**: Code quality and complexity assessment
5. **Quick Tip**: One concrete, actionable improvement

Be concise and developer-friendly. Use bullet points inside sections where helpful.

Code:
```{language}
{code}
```"""


# ── RAG Service ───────────────────────────────────────────────────────────────

class RAGService:
    def __init__(self):
        self.settings = get_settings()
        self.embeddings = OpenAIEmbeddings(
            model=self.settings.openai_embedding_model,
            api_key=self.settings.openai_api_key,
        )
        self.llm = ChatOpenAI(
            model=self.settings.openai_model,
            api_key=self.settings.openai_api_key,
            max_tokens=self.settings.max_tokens,
            temperature=0.3,
        )

    def _build_vector_store(self, code: str, filename: str) -> FAISS:
        safe_code = truncate_code(code)
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
            separators=["\n\nclass ", "\n\ndef ", "\n\n", "\n", " ", ""],
        )
        chunks = splitter.create_documents(
            texts=[safe_code],
            metadatas=[{"filename": filename, "chunk": i} for i in range(1000)],
        )
        if not chunks:
            raise ValueError("Could not split code into chunks.")
        return FAISS.from_documents(chunks, self.embeddings)

    def _convert_history(self, chat_history: list[dict]) -> list:
        messages = []
        for msg in chat_history:
            if msg.get("role") == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg.get("role") == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        return messages

    async def chat(self, question: str, code: str, filename: str, language: str, chat_history: list[dict]) -> dict:
        # Step 1: Check for casual intent — instant reply, no embedding cost
        casual = detect_casual(question)
        if casual:
            logger.info(f"Casual message '{question}' — skipping RAG")
            return {"answer": casual, "sources": []}

        # Step 2: Real code question — run full RAG pipeline
        logger.info(f"Code question '{question[:60]}' — running RAG")
        vector_store = self._build_vector_store(code, filename)
        retriever = vector_store.as_retriever(search_kwargs={"k": self.settings.top_k_results})
        chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            combine_docs_chain_kwargs={"prompt": CODE_QA_PROMPT},
            return_source_documents=True,
            verbose=False,
        )
        history = self._convert_history(chat_history)
        result = chain.invoke({"question": question, "chat_history": history})
        sources = [doc.page_content[:200] + "..." for doc in result.get("source_documents", [])[:3]]
        return {"answer": result["answer"], "sources": sources}

    async def summarize(self, code: str, filename: str, language: str) -> str:
        safe_code = truncate_code(code, max_chars=8000)
        prompt = SUMMARY_PROMPT.format(language=language, filename=filename, code=safe_code)
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content
