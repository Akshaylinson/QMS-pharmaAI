from app.core.config import settings
from app.ai.providers.base import BaseLLMProvider
class GroqProvider(BaseLLMProvider):
    name='groq'
    def structured(self, prompt, schema):
        from langchain_groq import ChatGroq
        return ChatGroq(model=settings.groq_model, api_key=settings.groq_api_key, temperature=0).with_structured_output(schema).invoke(prompt)
class GeminiProvider(BaseLLMProvider):
    name='gemini'
    def structured(self, prompt, schema):
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(model=settings.gemini_model, google_api_key=settings.gemini_api_key, temperature=0).with_structured_output(schema).invoke(prompt)
def get_llm_provider() -> BaseLLMProvider | None:
    if settings.llm_provider.lower() == 'gemini' and settings.gemini_api_key: return GeminiProvider()
    if settings.llm_provider.lower() == 'groq' and settings.groq_api_key: return GroqProvider()
    return None
