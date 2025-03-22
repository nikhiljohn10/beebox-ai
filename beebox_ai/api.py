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
        return (
            "You are an AI that helps generate 3D models and manipulate them via "
            "Blender's Python API. Provide very efficient and error free python "
            "script only as result. Do not encapsulate the code with triple quotes."
            "Provide documentation using inline comments. Never reply with any non-code"
            " information. Do not use any external libraries. Do not delete existing objects."
        )

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
            max_tokens=4096,
            temperature=1.0,
            top_p=1.0,
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

