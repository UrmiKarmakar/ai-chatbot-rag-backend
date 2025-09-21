# chat/ai_services.py
import time
import logging
from typing import List, Dict, Optional
import google.generativeai as genai
from decouple import config

logger = logging.getLogger(__name__)


class AIService:
    """
    Gemini wrapper for chat-style generation with RAG context.
    Expects history as a list of dicts:
        [{"role": "user"/"assistant", "content": "..."}]
    """

    def __init__(self, model_name: Optional[str] = None):
        api_key = config("GEMINI_API_KEY", default="")
        if not api_key:
            logger.error("GEMINI_API_KEY not set — AIService disabled.")
            self.model = None
            return

        # Configure Gemini client
        genai.configure(api_key=api_key)

        self.model_name = model_name or config("GEMINI_MODEL", default="gemini-2.5-flash")
        self.temperature = float(config("GEMINI_TEMPERATURE", default="0.7"))
        self.max_tokens = int(config("GEMINI_MAX_TOKENS", default="512"))

        try:
            self.model = genai.GenerativeModel(self.model_name)
            logger.info("AIService initialized with model: %s", self.model_name)
        except Exception as e:
            logger.error("Failed to initialize Gemini model: %s", e)
            self.model = None

    def generate_response(
        self, query: str, context: str = "", history: Optional[List[Dict]] = None
    ) -> str:
        """
        Generate a response using Gemini with RAG context and optional history.
        - query:   the user’s question
        - context: retrieved chunks from FAISS
        - history: list of previous messages [{"role": "user"/"assistant", "content": "..."}]
        """
        if not self.model:
            return "AI service is not configured."

        if history is None:
            history = []

        messages = []

        # Add conversation history (map assistant → model)
        for msg in history:
            role = msg.get("role", "user")
            if role == "assistant":
                role = "model"
            elif role != "user":
                role = "user"
            content = msg.get("content", "")
            if content:
                messages.append({"role": role, "parts": [{"text": content}]})

        # Build query with context instructions
        if context:
            full_query = (
                "You are a helpful assistant for an e-commerce chatbot.\n"
                "Use only the following context to answer the user's question.\n"
                "If the answer is not in the context, say politely that you don't know.\n"
                "Do not invent information. Be concise, clear, and professional.\n\n"
                f"Context:\n{context}\n\n"
                f"User question: {query}"
            )
        else:
            full_query = query

        # Add current user query
        messages.append({"role": "user", "parts": [{"text": full_query}]})

        # Retry loop for robustness
        for attempt in range(3):
            try:
                resp = self.model.generate_content(
                    messages,
                    generation_config={
                        "temperature": self.temperature,
                        "max_output_tokens": self.max_tokens,
                    },
                )
                text = (resp.text or "").strip()
                if text:
                    return text
                return "I couldn't generate a response."
            except Exception as e:
                logger.warning("Gemini API attempt %s failed: %s", attempt + 1, e)
                time.sleep(1)

        return "Sorry, I had trouble generating a response. Please try again later."


# Singleton instance for reuse
ai_service = AIService()
