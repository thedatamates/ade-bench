from abc import ABC, abstractmethod


class ContextLengthExceededError(Exception):
    """Raised when the LLM response indicates the context length was exceeded."""

    pass


class ParseError(Exception):
    """Raised when the LLM response cannot be parsed into the expected format."""

    pass


class BaseLLM(ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @abstractmethod
    def call(self, prompt: str, **kwargs) -> str:
        pass

    @abstractmethod
    def count_tokens(self, messages: list[dict]) -> int:
        pass
