# chat/ai_services.py
import time
import logging
from typing import List, Dict
import google.generativeai as genai
from decouple import config

logger = logging.getLogger(__name__)


class AIService:
    """
    Gemini wrapper for chat-style generation with RAG context.
    Expects history as [{"role": "user"/"assistant", "content": "..."}].
    """

    def __init__(self, model_name: str = None):
        api_key = config("GEMINI_API_KEY", default="")
        if not api_key:
            logger.error("GEMINI_API_KEY not set — AIService disabled.")
            self.model = None
            return

        genai.configure(api_key=api_key)

        self.model_name = model_name or config("GEMINI_MODEL", default="gemini-2.5-flash")
        self.temperature = float(config("GEMINI_TEMPERATURE", default="0.7"))
        self.max_tokens = int(config("GEMINI_MAX_TOKENS", default="512"))

        self.model = genai.GenerativeModel(self.model_name)

    def generate_response(self, query: str, context: str, history: List[Dict]) -> str:
        """
        Build messages with a strong system instruction containing RAG context,
        followed by history, then the user message.
        """
        if not self.model:
            return "AI service is not configured."

        messages = []

        if context:
            system_prompt = (
                "You are a helpful assistant for an e-commerce chatbot.\n"
                "Use only the following context to answer the user's question.\n"
                "If the answer is not in the context, say politely that you don't know.\n"
                "Do not invent information. Be concise, clear, and professional.\n\n"
                f"Context:\n{context}"
            )
            messages.append({"role": "system", "parts": [system_prompt]})

        for msg in history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if content:
                messages.append({"role": role, "parts": [content]})

        messages.append({"role": "user", "parts": [query]})

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
                return text or "I couldn't generate a response."
            except Exception as e:
                logger.warning("Gemini API attempt %s failed: %s", attempt + 1, e)
                time.sleep(1)

        return "Sorry, I had trouble generating a response. Please try again later."


ai_service = AIService()
