import bpy
import asyncio
from . import api
from .services import get_openai_client
from .utils import error_popup, get_preferences, ScriptFile


class BEEBOXAI_OT_send_message(bpy.types.Operator):
    bl_idname = "beebox_ai.send_message"
    bl_label = "BeeBox AI send message via API"
    bl_options = {"REGISTER", "UNDO"}

    async def stream(self, context, prompt):
        error = ""
        try:
            file = ScriptFile(context)
            if context.scene.beebox_ai_reset:
                file.clear_text()
            elif file.is_not_empty():
                file.write("\n\n")

            if get_preferences().comment_prompt:
                file.write("# Prompt: " + prompt + "\n\n")

            client = get_openai_client()
            try:
                await client.stream(file.write, prompt)
            except api.APIConnectionError as e:
                error = f"The OpenAI server could not be reached: {e.__cause__}"
            except api.AuthenticationError as e:
                error = (
                    "Your not allow to access this resource. \n"
                    "There might be an issue with your API key. \n"
                    "Please see preferences."
                )
            except api.RateLimitError as e:
                error = "Your OpenAI quota has been exceeded"
            except api.APIStatusError as e:
                error = f"Error found in the API response from OpenAI.\nSTATUS = {e.status_code} | ERROR = {e.response}"
            except api.PermissionDeniedError as e:
                error = f"Permission Error: {e}"
        except AttributeError as e:
            error = f"API Input Error: {e}"
        except RuntimeError as e:
            error = f"Runtime Error: {e}"
        except Exception as e:
            error = f"Error in stream: {e}"

        if error != "":
            error_popup(error)

    def execute(self, context):
        input_text = context.scene.beebox_ai_prompt
        if input_text == "":
            return {"CANCELLED"}

        task = asyncio.ensure_future(self.stream(context, input_text))
        try:
            asyncio.get_event_loop().run_until_complete(task)
        except api.PermissionDeniedError as e:
            print("Permission Error:", e)
        except api.APIConnectionError as e:
            print("Connection Error:", e)
        except api.APIError as e:
            print("API Error:", e)
        except Exception as e:
            print("Exception:", e)
        else:
            return {"FINISHED"}
        return {"CANCELLED"}
