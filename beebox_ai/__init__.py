'''
BeeBox AI - An AI tool for creating 3D models and manipulating them by generating python scripts inside Blender's Script Editor.

Copyright (C) 2025 Nikhil John

This program is free software: you can redistribute it and/or modify it under 
the terms of the GNU General Public License as published by the Free Software 
Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY 
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A 
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this 
program. If not, see <https://www.gnu.org/licenses/>.
'''

import bpy

from .requirement import install_packages

PACKAGE_NAME = __package__
REQUIRED_PACKAGES = {
    # module name: version
    "openai": "==1.68.2",
}

def add_ai_input(self, context):
    layout = self.layout
    layout.prop(context.scene, "ai_text_input")


def on_input_enter(self, context):
    if context.scene.ai_text_input != "":
        bpy.ops.beebox_ai.send_message()
        context.scene.ai_text_input = ""


def register():
    install_packages(REQUIRED_PACKAGES)
    bpy.types.Scene.ai_text_input = bpy.props.StringProperty(
        name="AI Prompt",
        description="Input for AI text",
        default="",
        update=on_input_enter,
    )
    from .preferences import BEEBOXAI_Preferences
    bpy.utils.register_class(BEEBOXAI_Preferences)
    from .operators import BEEBOXAI_OT_send_message
    bpy.utils.register_class(BEEBOXAI_OT_send_message)
    bpy.types.TEXT_HT_header.append(add_ai_input)


def unregister():
    bpy.types.TEXT_HT_header.remove(add_ai_input)
    from .operators import BEEBOXAI_OT_send_message
    bpy.utils.unregister_class(BEEBOXAI_OT_send_message)
    from .preferences import BEEBOXAI_Preferences
    bpy.utils.unregister_class(BEEBOXAI_Preferences)
    del bpy.types.Scene.ai_text_input


if __name__ == "__main__":
    install_packages(REQUIRED_PACKAGES)
    register()
