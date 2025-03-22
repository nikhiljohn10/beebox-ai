import bpy
from openai import AsyncAzureOpenAI
from bpy.props import (  # type: ignore
    StringProperty
)


from .abstract import Service
from ..utils import get_preferences
from ..api import APIUtils


class AzureOpenAiAPI(Service, APIUtils):
    service_item = ("AZUREOPENAI", "Azure OpenAI", "Settings for Azure OpenAI")

    def __init__(self):
        super(APIUtils, self).__init__()
        pref = get_preferences()
        if pref.azure_api_key == "":
            raise AttributeError("AzureOpenAI API key is required")
        if pref.azure_base_url == "":
            raise AttributeError("AzureOpenAI base URL is required")
        if pref.azure_deployment_name == "":
            raise AttributeError("AzureOpenAI deployment name is required")
        if pref.azure_api_version == "":
            raise AttributeError("AzureOpenAI api version is required")
        self.model = pref.azure_deployment_name
        self.client = AsyncAzureOpenAI(
            api_version=pref.azure_api_version,
            azure_endpoint=pref.azure_base_url,
            api_key=pref.azure_api_key,
            timeout=self.timeout,
        )

    @staticmethod
    def preference_layout(self, layout):
        layout.prop(self, "azure_api_version", placeholder="2024-10-21")
        layout.prop(self, "azure_base_url", placeholder="https://<resource_name>.openai.azure.com/")
        layout.prop(self, "azure_deployment_name", placeholder="gpt-4o")
        layout.prop(self, "azure_api_key", placeholder="****************")

class AzureOpenAIProperties:

    azure_base_url: StringProperty(
        name="Base URL",
        default="https://resource_name.openai.azure.com/",
    )

    azure_api_version: StringProperty(
        name="API Version",
        default="2024-10-21",
    )

    azure_deployment_name: StringProperty(
        name="Deployment Name",
    )

    azure_api_key: StringProperty(
        name="API Key",
        subtype="PASSWORD",
    )