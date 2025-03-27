import bpy
import httpx
from openai.lib.azure import BaseClient
from openai import (
    APIConnectionError,
    RateLimitError,
    APIStatusError,
    AuthenticationError,
    PermissionDeniedError,
    APIError,
)

from .utils import Message, ScriptFile, get_preferences

Client = BaseClient


class APIUtils:
    model: str
    client: Client
    timeout = httpx.Timeout(60.0, read=5.0, write=10.0, connect=2.0)

    async def close(self):
        await self.client.close()

    def run_script(self):
        if get_preferences().run_script:
            bpy.ops.text.run_script()

    def preprocess(self, file: ScriptFile, prompt: str):
        code = None
        pref = get_preferences()
        if file.is_not_empty and pref.include_code:
            code = file.selected_text if file.is_selected else file.text
        if not file.is_selected:
            file.move_cursor_last()
        file.write("\n")
        return code

    def _instruction(self, file: ScriptFile, code: str):
        instruction = """
Given a task description, produce a detailed Python code using Blender's "bpy" module (version 4.3.0) under Python 3.11 to complete the task effectively. Follow these guidelines:

1. Understand the Task
    - Grasp the main objective, goals, requirements, constraints, and expected output.
    - Generate or manipulate 3D models (or perform other related actions) in Blender based on the task description.

2. Minimal Changes
    - If existing code is present, improve it only if it is simple.
    - For complex tasks, clarify and add missing elements without altering the original structure.

3. Clarity and Conciseness
    - Use clear, specific language to comment the code.
    - Avoid unnecessary instructions or redundant statements.

4. Formatting
    - Follow Python’s PEP 8 style.
    - Do not include any additional commentary in the output (e.g., no separators like "---").
    - Do not wrap the output code in triple quotes or Markdown formatting.

5. Error Handling
    - Ensure the code runs without issues.
    - Include exception handling if necessary.

6. Documentation
    - Provide inline comments explaining the code logic and functionality.
    - Describe the purpose of each function, method, or block of code.
7. Reusability
    - Write modular code using functions and classes where appropriate.
    - Ensure it is easily adaptable for similar tasks.

8. Efficiency
    - Optimize for performance and resource usage.
    - Use efficient methods and algorithms.

9. Output Format
    - Include only the Python code required for the solution.
    - Adhere strictly to Python 3.11 and bpy 4.3.0 with no external libraries.
    - Do not delete existing objects in the scene.

10. Blender Script Editor Addon Context
    - This code will be appended to existing code in the Blender Script Editor.
    - If a module is already imported, do not re-import it.
    - Ignore all comments in the existing code and focus only on its logic and structure.
"""
        if code is not None and get_preferences().include_code:
            instruction += "\n\n11. When existing code is present"
            if file.is_selected:
                instruction += (
                    "\n\t- Existing code is to be replaced by output code by the addon."
                )
            else:
                instruction += "\n\t- Output code is to be appended to the end of existing code by the addon."

        instruction += "\n\nEnsure the final output is strictly the Python code fulfilling the above requirements, with no additional text or messages."
        return instruction

    async def stream(self, context: bpy.types.Context, prompt: str):
        if self.client is None:
            raise ModuleNotFoundError("Client is not found")

        code = None
        file = ScriptFile(context)
        if context.scene.beebox_ai_reset:
            file.clear_text()
        else:
            code = self.preprocess(file, prompt)
        messages = Message(self._instruction(file, code))
        if code is not None:
            messages.add_user_message(code)
        messages.add_user_message(prompt)

        if get_preferences().comment_prompt:
            file.write("# Prompt: " + prompt + "\n\n")

        async with self.client.beta.chat.completions.stream(
            messages=messages(),
            max_tokens=8192,
            temperature=0.2,
            top_p=0.1,
            model=self.model,
        ) as stream:

            async for event in stream:
                if event.type == "chunk":
                    try:
                        content = event.chunk.choices[0].delta.content
                        if content is not None:
                            file.write(content)
                    except IndexError:
                        pass
                elif event.type == "content.done":
                    self.run_script()
                    break
                elif event.type == "error":
                    print("Error in stream:", event.error)
                    break
