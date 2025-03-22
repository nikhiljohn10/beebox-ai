import bpy

from .services.openai import OpenAiAPI, OpenAIProperties
from .services.azure_openai import AzureOpenAiAPI, AzureOpenAIProperties
from bpy.props import (  # type: ignore
    EnumProperty,
    BoolProperty,
)


class BEEBOXAI_Preferences(bpy.types.AddonPreferences, OpenAIProperties, AzureOpenAIProperties):
    bl_idname = __package__

    tab: EnumProperty(
        name="Settings",
        description="BeeBox AI Settings",
        items=[
            ("GENERAL", "General", "General Settings"),
            ("AI_SERVICE", "AI Service", "AI Service Settings"),
        ],
        default="GENERAL",
    )

    ai_serive: EnumProperty(
        name="AI Serive",
        description="Choose the AI service",
        items=[
            # OpenAiAPI.service_item,
            AzureOpenAiAPI.service_item,
        ],
        default="AZUREOPENAI",
    )

    run_script: BoolProperty(
        name="Run Script",
        description="Run the script after generating",
        default=False,
    )

    def draw_general(self, layout):
        layout.label(text="General Settings:")
        layout.prop(self, "run_script")

    def draw_ai_service(self, layout):
        row = layout.row()
        row.label(text="Choose your AI Service:")
        row.prop(self, "ai_serive", expand=True)

        box = layout.box()
        row = box.row()
        col = row.column()
        if self.ai_serive == "OPENAI":
            OpenAiAPI.preference_layout(self, col)
        else:
            AzureOpenAiAPI.preference_layout(self, col)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "tab", expand=True)
        box = layout.box()

        if self.tab != "AI_SERVICE":
            self.draw_general(box)
        else:
            self.draw_ai_service(box)
