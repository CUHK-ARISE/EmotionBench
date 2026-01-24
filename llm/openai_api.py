import os
import time
from typing import List, Optional

from openai import OpenAI
from llm import LLMChat, Message


class OpenAIChat(LLMChat):
    def __init__(self, model_name: str, client: Optional[OpenAI] = None, **kwargs) -> None:
        if client is None:
            openai_client = OpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
            )
        self.client = client or openai_client
        super().__init__(model_name, **kwargs)
    
    def get_msg(self, messages: List[Message]) -> List[dict]:
        message_list = [msg.to_openai_format() for msg in messages]
        return message_list
    
    def chat_reasoning_model(self, input_prompt: List[dict], n: int) -> List[str]:
        """For reasoning models (GPT-5, O-series) using responses.create() API"""
        # Convert messages to input string (use the last user message)
        user_message = None
        for msg in reversed(input_prompt):
            if msg["role"] == "user":
                user_message = msg["content"]
                break
        
        if user_message is None:
            raise ValueError("No user message found in input_prompt")
        
        response = self.client.responses.create(
            model=self.model_name,
            input=user_message,
            **self.get_openai_conf(n=n)
        )
        
        response_text = response.output[1].content[0].text
        self.write_records(response_text, title="RESPONSE")
        time.sleep(self.delay)
        return [response_text]
    
    def chat_generic(self, input_prompt: List[dict]) -> List[str]:
        responses = self.client.chat.completions.create(
            model=self.model_name,
            messages=input_prompt,
            **self.get_openai_conf(n=1)
        )
        self.write_records(responses.choices[0].message.content, title="RESPONSE")
        time.sleep(self.delay)
        return [c.message.content for c in responses.choices]
    
    
    def chat_streaming(self, input_prompt: List[dict], n: int, stream_print: bool) -> List[str]:
        response_stream = self.client.chat.completions.create(
            model=self.model_name,
            messages=input_prompt,
            stream=True,
            **self.get_openai_conf(n=n),
        )
        
        response_content = ""
        reasoning_content = ""
        
        for chunk in response_stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            if hasattr(delta, "reasoning_content") and delta.reasoning_content != None:
                reasoning_content += delta.reasoning_content
                if stream_print:
                    print(delta.reasoning_content, end="", flush=True)
            else:
                response_content += delta.content
                if stream_print:
                    print(delta.content, end="", flush=True)
            
        self.write_records(reasoning_content, title="RESPONSE")
        time.sleep(self.delay)
        
        if reasoning_content == "":
            return [response_content]
        else:
            return [f"<think>{reasoning_content}</think>\n\n{response_content}"]
    
    
    def chat(self, messages: List[Message], n: int = 1, stream_print: bool = False) -> List[str]:
        input_prompt = self.get_msg(messages)
        self.write_records(messages[-1].content, title="INPUT")
        
        # Check if it's a reasoning model that should use responses.create()
        is_reasoning_model = self.model_name in ["o1", "o3", "o3-mini", "o4-mini", "gpt-5", "gpt-5-mini", "gpt-5-nano", "gpt-5.1"]
        
        if is_reasoning_model:
            return self.chat_reasoning_model(input_prompt, n)
        elif self.stream:
            return self.chat_streaming(input_prompt, n, stream_print)
        else:
            return self.chat_generic(input_prompt)
