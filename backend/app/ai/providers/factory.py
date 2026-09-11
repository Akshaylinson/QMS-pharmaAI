from app.core.config import settings
from app.ai.providers.base import BaseLLMProvider
from urllib.parse import urlparse
class GroqProvider(BaseLLMProvider):
    name='groq'
    def structured(self, prompt, schema):
        from langchain_groq import ChatGroq
        # A provider outage must not leave the intake UI waiting forever. The
        # graph catches provider failures and uses its local evidence parser.
        return ChatGroq(model=settings.groq_model, api_key=settings.groq_api_key, temperature=0, timeout=15, max_retries=0).with_structured_output(schema, method='json_mode').invoke(prompt)
class GeminiProvider(BaseLLMProvider):
    name='gemini'
    def structured(self, prompt, schema):
        from langchain_google_genai import ChatGoogleGenerativeAI
        parsed=urlparse(settings.gemini_base_url)
        endpoint=parsed.netloc or parsed.path
        client_options={'api_endpoint':endpoint} if endpoint else None
        models=[]
        for model in (settings.gemini_model, settings.gemini_fallback_model):
            if model and model not in models: models.append(model)
        last_error=None
        for model in models:
            try:
                return ChatGoogleGenerativeAI(model=model, google_api_key=settings.gemini_api_key, temperature=0, timeout=15, max_retries=0, client_options=client_options).with_structured_output(schema).invoke(prompt)
            except Exception as error:
                last_error=error
        raise last_error or RuntimeError('No Gemini model is configured.')
def get_llm_provider() -> BaseLLMProvider | None:
    if settings.llm_provider.lower() == 'gemini' and settings.gemini_api_key: return GeminiProvider()
    if settings.llm_provider.lower() == 'groq' and settings.groq_api_key: return GroqProvider()
    return None
