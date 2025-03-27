import bpy


class ScriptFile:
    def __init__(self, context):
        self._file = self.get(context)
        if self._file is None:
            bpy.ops.text.new()
            self._file = self.get(context)

    @property
    def text(self):
        return self._file.as_string()

    @property
    def selected_text(self):
        return self._file.region_as_string()

    @property
    def is_selected(self):
        return self.selected_text != ""

    @property
    def is_active(self):
        return self._file is not None

    @property
    def is_not_empty(self):
        return len(self._file.as_string()) > 0
    
    @property
    def current_cursor(self):
        return self._file.current_character, self._file.current_line_index

    def write(self, text):
        if self.is_active:
            bpy.data.texts[self._file.name].region_from_string(text)

    def move_cursor_last(self):
        if self.is_active:
            self._file.cursor_set(
                line=len(self._file.lines) - 1,
                character=len(self._file.lines.values()[-1].body),
            )

    def clear_text(self):
        if self.is_active:
            self._file.clear()

    def delete_selection(self):
        if self.is_active:
            self._file.region_from_string("")

    @staticmethod
    def get(context):
        for area in context.screen.areas:
            if area.type == "TEXT_EDITOR":
                return area.spaces.active.text
        return None

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


class Message:
    def __init__(self, system_instruction):
        self.messages = [
            {
                "role": "system",
                "content": system_instruction,
            }
        ]

    def add_user_message(self, prompt):
        self.messages.append({"role": "user", "content": prompt})

    def __call__(self):
        return self.messages


def error_popup(error):
    def draw_popup(self, context):
        self.layout.label(text=error)

    bpy.context.window_manager.popup_menu(draw_popup, title="Error", icon="ERROR")


def get_package_name():
    return __package__


def get_preferences():
    return bpy.context.preferences.addons[__package__].preferences
