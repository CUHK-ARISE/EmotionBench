import os
import time
import anthropic
from typing import List, Union, Optional, Tuple
from tenacity import (retry, stop_after_attempt, wait_random_exponential)

from llm import LLMChat, Message

class AnthropicChat(LLMChat):
    client = anthropic.Anthropic(
        api_key=os.getenv(f"ANTHROPIC_API_KEY")
    )
    
    def __init__(self, model_name:str, **kwargs) -> None:
        super().__init__(model_name, **kwargs)
    
    def get_msg(self, messages: List["Message"]) -> Tuple[Optional[str], List[dict]]:
        formatted_messages = [msg.to_openai_format() for msg in messages]
        system_msg = None
        if formatted_messages and formatted_messages[0]["role"] == "system":
            system_msg = formatted_messages.pop(0)["content"]
        return system_msg, formatted_messages
    
    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def chat(self, messages: List[Message], n: int = 1) -> Union[List[str], str]:
        
        system_msg, input_prompt = self.get_msg(messages)
        self.write_records(messages[-1].content, title="INPUT")
        
        response = self.client.messages.create(
            model=self.model_name,
            messages=input_prompt,
            **self.get_anthropic_conf(system_msg=system_msg)
        )
        
        self.write_records(response.content[0].text, title="RESPONSE")
        time.sleep(self.delay)
        return [response.content[0].text]
