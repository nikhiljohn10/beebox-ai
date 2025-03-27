import bpy

class ScriptFile:
    def __init__(self, context):
        self._file = self.get(context)
        if self._file is None:
            bpy.ops.text.new()
            self._file = self.get(context)

    @staticmethod
    def get(context):
        for area in context.screen.areas:
            if area.type == "TEXT_EDITOR":
                return area.spaces.active.text
        return None
    
    def is_active(self):
        return self._file is not None
    
    def is_not_empty(self):
        return len(self._file.as_string()) > 0

    def write(self, text):
        if self.is_active:
            bpy.data.texts[self._file.name].write(text)

    def clear_text(self):
        if self.is_active:
            self._file.clear()
    
    @staticmethod
    def delete_all():
        for text_block in bpy.data.texts:
            bpy.data.texts.remove(text_block)

    @classmethod
    def delete_active_file(cls, context):
        bpy.data.texts.remove(cls.get(context))

    def delete(self):
        if self.is_active:
            bpy.data.texts.remove(self._file)
            self._file = None

def error_popup(error):
    def draw_popup(self, context):
        self.layout.label(text=error)

    bpy.context.window_manager.popup_menu(
        draw_popup, title="Error", icon="ERROR"
    )

def get_package_name():
    return __package__

def get_preferences():
    return bpy.context.preferences.addons[__package__].preferences