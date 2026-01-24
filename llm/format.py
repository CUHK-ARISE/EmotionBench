import dataclasses
from typing import Literal

Roles = Literal["system", "user", "assistant"]


@dataclasses.dataclass()
class Message:
    role: Roles
    content: str
    
    def to_openai_format(self):
        return {"role": self.role, "content": self.content.strip()}
    
    def to_gemini_format(self):
        gemini_role = {"system": "user", "assistant": "model"}.get(self.role, "user")
        return { "role": gemini_role, "parts": [self.content.strip()]}
    