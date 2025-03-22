from .azure_openai import AzureOpenAiAPI
from .openai import OpenAiAPI
from ..utils import get_preferences

def get_openai_client():
    if get_preferences().ai_serive == "OPENAI":
        return OpenAiAPI()
    return AzureOpenAiAPI()

