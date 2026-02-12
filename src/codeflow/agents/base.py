"""Base class for all AI agents."""

import logging
from abc import ABC, abstractmethod
from typing import Any

from groq import Groq

from ..core.config import get_settings

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all AI agents in the system."""

    def __init__(self, model: str = "llama-3.3-70b-versatile") -> None:
        """Initialize the agent.

        Args:
            model: The Groq model to use. Default is Llama 3.3 70B.
        """
        self.settings = get_settings()
        self.model = model
        self.client = Groq(api_key=self.settings.groq_api_key)
        logger.info(f"Initialized {self.__class__.__name__} with model {model}")

    @abstractmethod
    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Process input and return results.

        This method must be implemented by all agent subclasses.

        Args:
            input_data: Input data for the agent to process

        Returns:
            Processed results as a dictionary
        """
        pass

    def _create_chat_completion(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 2000,
    ) -> str:
        """Create a chat completion using Groq.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0.0-2.0). Lower = more focused
            max_tokens: Maximum tokens in response

        Returns:
            The model's response content
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content
            logger.debug(f"LLM response: {content[:100]}...")
            return content

        except Exception as e:
            logger.error(f"Error calling Groq API: {e}", exc_info=True)
            raise
