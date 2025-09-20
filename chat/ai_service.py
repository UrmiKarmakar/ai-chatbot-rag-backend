import os
import time
import logging
from typing import List, Dict
import google.generativeai as genai

logger = logging.getLogger(__name__)


class AIService:
    """
    Gemini wrapper for chat-style generation with RAG context.
    Expects history as [{"role": "user"/"assistant"/"system", "content": "..."}].
    """

    def __init__(self, model_name: str = None):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY not set — AIService disabled.")
            self.model = None
            return

        genai.configure(api_key=api_key)

        # Choose fast or deep model based on env or default
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.temperature = float(os.getenv("GEMINI_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("GEMINI_MAX_TOKENS", "512"))

        self.model = genai.GenerativeModel(self.model_name)

    def generate_response(self, query: str, context: str, history: List[Dict]) -> str:
        """
        Build messages with a system-like first message containing RAG context,
        followed by history, then the user message.
        """
        if not self.model:
            return "AI service is not configured."

        messages = []

        if context:
            messages.append({"role": "system", "parts": [context]})

        for msg in history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if content:
                messages.append({"role": role, "parts": [content]})

        messages.append({"role": "user", "parts": [query]})

        # Retry loop for resilience
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
