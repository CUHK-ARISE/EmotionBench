import os
from typing import List, Union

from llm.format import Message

from dotenv import load_dotenv
load_dotenv(override=True)


class LLMChat():
    DEFAULT_MAX_TOKENS = 2048
    DEFAULT_TEMPERATURE = 0.0
    DEFAULT_DELAY = 0
    DEFAULT_TOP_P = 0.95
    DEFAULT_STREAM = False
    DEFAULT_TIMEOUT = 120
    DEFAULT_REASONING_EFFORT = "minimal"
    
    def __init__(self, model_name: str, **kwargs) -> None:
        """
        1. temperature
        2. max_tokens
        3. top_p
        4. delay
        5. max_n
        6. stream
        7. timeout
        8. reasoning_effort
        """
        self.model_name = model_name
        self.folder_name = kwargs.get("folder_name")
        if self.folder_name is None:
            self.folder_name = model_name.replace("/", "-")
        self.max_tokens = kwargs.get("max_tokens", self.DEFAULT_MAX_TOKENS)
        self.temperature = kwargs.get("temperature", self.DEFAULT_TEMPERATURE)
        self.top_p = kwargs.get("top_p", self.DEFAULT_TOP_P)
        self.delay = kwargs.get("delay", self.DEFAULT_DELAY)
        self.max_n = kwargs.get("max_n")
        self.stream = kwargs.get("stream", self.DEFAULT_STREAM)
        self.timeout = kwargs.get("timeout", self.DEFAULT_TIMEOUT)
        self.reasoning_effort = kwargs.get("reasoning_effort", self.DEFAULT_REASONING_EFFORT)

    
    def get_openai_conf(self, n: int) -> dict[str]:
        n = min(self.max_n, n) if self.max_n else n
        n = 1 if self.stream else n
        
        if self.model_name in ["o1", "o3", "o3-mini", "o4-mini", "gpt-5", "gpt-5-mini", "gpt-5-nano"]:
            config = {
                "max_output_tokens": self.max_tokens,
                "timeout": self.timeout,
                "reasoning": {"effort": self.reasoning_effort}
            }
        elif self.model_name in ["gemini-2.5-pro", "gemini-3-pro-preview"]:
            config = {
                "n": n,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "reasoning_effort": "low",
                "timeout": self.timeout,
            }
        else:
            config = {
                "n": n,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "timeout": self.timeout,
            }
        return config
    
    
    def get_gemini_conf(self, n: int) -> dict[str]:
        if self.max_n: n = min(self.max_n, n)
        return {
            "candidate_count": n,
            "max_output_tokens": self.max_tokens,
            "temperature": self.temperature,
        }
    
    
    def get_anthropic_conf(self, system_msg: str = None) -> dict[str]:
        if self.model_name in ["claude-sonnet-4-5-20250929"]:
            config = {
                "max_tokens": self.max_tokens,
                "thinking": {
                    "type": "disabled",
                }
            }
        else:
            config = {
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "top_p": self.top_p,
                "thinking": {
                    "type": "disabled"
                }
            }
        if system_msg:
            config["system"] = system_msg
        return config
    
    def chat(
        self,
        messages: List[Message],
        n: int = 1,
    ) -> Union[List[str], str]:
        pass
    
    def write_records(self, message: str, title: str = "LOGS", file: str = "logs") -> None:
        os.makedirs(file, exist_ok=True)
        with open(f"./{file}/records.txt", "a") as record_file:
            if title == "LOGS":
                record_file.write(f"================================ {title} ================================\n")
            else:
                record_file.write(f"-------------------------------- {title} --------------------------------\n")
            record_file.write(str(message) + "\n")
    
    def get_msg(self):
        pass
