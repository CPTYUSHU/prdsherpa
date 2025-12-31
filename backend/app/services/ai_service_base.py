"""
Abstract base class for AI services.
Defines unified interface for different AI providers (Gemini, OpenAI, Claude).
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, AsyncGenerator
from dataclasses import dataclass
from datetime import datetime


@dataclass
class AIUsageStats:
    """Statistics for AI API usage."""
    model_name: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost: float  # in USD
    timestamp: datetime


@dataclass
class AIMessage:
    """Standardized message format for AI conversations."""
    role: str  # "system", "user", "assistant"
    content: str
    images: Optional[List[str]] = None  # Image paths or URLs


class AIServiceBase(ABC):
    """
    Abstract base class for AI services.

    All AI provider implementations (Gemini, OpenAI, Claude) must implement this interface.
    This ensures consistent behavior across different AI models.
    """

    def __init__(self, model_name: str, api_key: str):
        """
        Initialize AI service.

        Args:
            model_name: Name of the AI model to use
            api_key: API key for the service
        """
        self.model_name = model_name
        self.api_key = api_key
        self._usage_stats: List[AIUsageStats] = []

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name (e.g., 'Gemini', 'OpenAI', 'Claude')."""
        pass

    @property
    @abstractmethod
    def supports_streaming(self) -> bool:
        """Return whether this service supports streaming responses."""
        pass

    @property
    @abstractmethod
    def supports_images(self) -> bool:
        """Return whether this service supports image inputs."""
        pass

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate text from a single prompt.

        Args:
            prompt: User prompt
            system_instruction: Optional system instruction
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text
        """
        pass

    @abstractmethod
    async def chat(
        self,
        messages: List[AIMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Chat with conversation history.

        Args:
            messages: List of conversation messages
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated response
        """
        pass

    @abstractmethod
    async def chat_stream(
        self,
        messages: List[AIMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Chat with streaming response.

        Args:
            messages: List of conversation messages
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate

        Yields:
            Chunks of generated response
        """
        pass

    @abstractmethod
    async def analyze_document(
        self,
        document_content: str,
        document_type: str,
        filename: str = "",
    ) -> Dict[str, Any]:
        """
        Analyze a document and extract structured information.

        Args:
            document_content: Document text content
            document_type: Type of document (e.g., "prd", "pdf", "pptx")
            filename: Original filename

        Returns:
            Structured analysis result
        """
        pass

    @abstractmethod
    async def analyze_image(
        self,
        image_path: str,
        prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Analyze an image and extract information.

        Args:
            image_path: Path to the image file
            prompt: Optional analysis prompt

        Returns:
            Structured analysis result
        """
        pass

    def record_usage(self, stats: AIUsageStats) -> None:
        """
        Record API usage statistics.

        Args:
            stats: Usage statistics to record
        """
        self._usage_stats.append(stats)

    def get_usage_stats(self) -> List[AIUsageStats]:
        """
        Get all recorded usage statistics.

        Returns:
            List of usage statistics
        """
        return self._usage_stats.copy()

    def get_total_cost(self) -> float:
        """
        Calculate total cost across all API calls.

        Returns:
            Total cost in USD
        """
        return sum(stat.estimated_cost for stat in self._usage_stats)

    def get_total_tokens(self) -> int:
        """
        Calculate total tokens used across all API calls.

        Returns:
            Total tokens used
        """
        return sum(stat.total_tokens for stat in self._usage_stats)

    @abstractmethod
    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """
        Estimate cost for given token usage.

        Args:
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens

        Returns:
            Estimated cost in USD
        """
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(model={self.model_name}, provider={self.provider_name})>"
