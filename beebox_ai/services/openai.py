import bpy
from openai import AsyncOpenAI
from bpy.props import (  # type: ignore
    StringProperty,
    EnumProperty
)


from .abstract import Service
from ..utils import get_preferences
from ..api import APIUtils


class OpenAiAPI(Service, APIUtils):
    service_item = ("OPENAI", "OpenAI", "Settings for OpenAI")

    def __init__(self):
        super(APIUtils, self).__init__()
        pref = get_preferences()
        if pref.openai_api_key == "":
            raise AttributeError("OpenAI API key is required")
        if pref.openai_model == "":
            raise AttributeError("OpenAI model is required")
        self.model = pref.openai_model
        self.client = AsyncOpenAI(
            api_key=pref.openai_api_key
        )
    
    @staticmethod
    def preference_layout(self, layout):
        layout.prop(self, "open_ai_model")
        layout.prop(self, "openai_api_key", placeholder="****************")


class OpenAIProperties:

    open_ai_model: EnumProperty(
        name="AI Model",
        description="Choose the AI model",
        items=[
            ("gpt-3", "GPT-3", "Use GPT-3 model"),
            ("gpt-4", "GPT-4", "Use GPT-4 model"),
            ("gpt-4o", "GPT-4o", "Use GPT-4o model"),
            ("gpt-4o-mini", "GPT-4o Mini", "Use GPT-4o Mini model"),
        ],
        default="gpt-4o-mini",
    )

    openai_api_key: StringProperty(
        name="API Key",
        subtype="PASSWORD",
    )

