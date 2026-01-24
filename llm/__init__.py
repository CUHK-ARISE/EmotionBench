from llm.base import LLMChat
from llm.format import Message
from llm.openai_api import OpenAIChat
from llm.platform_api import AzureChat, DeepInfraChat, DeepSeekChat, GeminiChat, QwenChat, TogetherAIChat, LMStudioChat, OpenKeyChat
from llm.anthropic_api import AnthropicChat


__all__ = [
    "LLMChat",
    "Message",
    "OpenAIChat",
    "AzureChat",
    "DeepInfraChat",
    "DeepSeekChat",
    "GeminiChat",
    "QwenChat",
    "TogetherAIChat",
    "LMStudioChat",
    "OpenKeyChat",
    "AnthropicChat",
]

def get_platform(platform: str) -> LLMChat:
    platform = platform.lower()
    if platform == "openai":
        return OpenAIChat
    elif platform == "azure":
        return AzureChat
    elif platform == "deepinfra":
        return DeepInfraChat
    elif platform == "deepseek":
        return DeepSeekChat
    elif platform == "gemini":
        return GeminiChat
    elif platform == "qwen":
        return QwenChat
    elif platform == "togetherai":
        return TogetherAIChat
    elif platform == "lmstudio":
        return LMStudioChat
    elif platform == "openkey":
        return OpenKeyChat
    elif platform == "anthropic":
        return AnthropicChat
    else:
        raise ValueError(f"Unsupported platform: {platform}")