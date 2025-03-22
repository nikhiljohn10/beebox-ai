import bpy

def error_popup(error):
    def draw_popup(self, context):
        self.layout.label(text=error)

    bpy.context.window_manager.popup_menu(
        draw_popup, title="Error", icon="ERROR"
    )

def get_textfile(context):
    for area in context.screen.areas:
        if area.type == "TEXT_EDITOR":
            return area.spaces.active.text
    return None

def get_package_name():
    return __package__

def get_preferences():
    return bpy.context.preferences.addons[__package__].preferences