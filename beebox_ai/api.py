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

from .utils import get_preferences

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

    @property
    def _instruction(self):
        return """
Given a task description, produce a detailed python code using Blender's 'bpy' module to complete the task effectively.

# Guidelines

- Understand the Task: Grasp the main objective, goals, requirements, constraints, and expected output. Then generate 3D models and manipulate them or carry out other related tasks in Blender.
- Minimal Changes: If an existing code is provided, improve it only if it's simple. For complex prompts, enhance clarity and add missing elements without altering the original structure.
- Clarity and Conciseness: Use clear, specific language to comment the code. Avoid unnecessary instructions or bland statements.
- Formatting: Use python PEP8 style. Do not include any additional commentary, only output the completed code. SPECIFICALLY, do not include any additional messages at the start or end of the code. (e.g. no "---")
- Error Handling: Ensure the code is error-free and runs without issues. Handle exceptions if necessary.
- Documentation: Include inline comments to explain the code logic and functionality. Describe the purpose of each function, method, or block of code.
- Reusability: Write modular code that can be reused for similar tasks in the future. Use functions and classes where appropriate.
- Efficiency: Optimize the code for performance and resource usage. Use the most efficient methods and algorithms to complete the task.
- Output Format: Python 3.11 code with documentation as inline comments. Use version 4.3.0 of bpy module. Do not use any external libraries. Do not delete existing objects.  Do not encapsulate the code with triple quotes. Never include any non-code related information or text.
"""

    async def stream(self, write: callable, prompt: str):
        if self.client is None:
            raise ModuleNotFoundError("Client is not found")
        async with self.client.beta.chat.completions.stream(
            messages=[
                {
                    "role": "system",
                    "content": self._instruction,
                },
                {"role": "user", "content": prompt},
            ],
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
                            write(content)
                    except IndexError:
                        pass
                elif event.type == "content.done":
                    self.run_script()
                    break
                elif event.type == "error":
                    print("Error in stream:", event.error)
                    break

