"""
AI Service Factory - manages AI service instances and model selection.
"""
from typing import Dict, Optional, Literal
from backend.app.services.ai_service_base import AIServiceBase
from backend.app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Type alias for AI providers
AIProvider = Literal["gemini", "openai", "claude", "deepseek"]


class AIServiceFactory:
    """
    Factory for creating and managing AI service instances.

    Features:
    - Singleton pattern for service instances
    - Model cost tracking
    - Provider switching
    - Configuration management
    """

    _instance: Optional["AIServiceFactory"] = None
    _services: Dict[str, AIServiceBase] = {}
    _current_provider: AIProvider = "gemini"

    def __new__(cls):
        """Singleton pattern - ensure only one factory instance exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the factory (only once due to singleton)."""
        if not hasattr(self, '_initialized'):
            self._initialized = True
            logger.info("AI Service Factory initialized")

    def get_service(self, provider: Optional[AIProvider] = None) -> AIServiceBase:
        """
        Get AI service instance for the specified provider.

        Args:
            provider: AI provider name ("gemini", "openai", "claude")
                     If None, uses the current provider

        Returns:
            AI service instance

        Raises:
            ValueError: If provider is not supported or not configured
        """
        if provider is None:
            provider = self._current_provider

        # Return cached instance if exists
        if provider in self._services:
            return self._services[provider]

        # Create new service instance
        service = self._create_service(provider)
        self._services[provider] = service

        logger.info(f"Created new AI service: {provider} ({service.model_name})")
        return service

    def _create_service(self, provider: AIProvider) -> AIServiceBase:
        """
        Create a new AI service instance based on provider.

        Args:
            provider: AI provider name

        Returns:
            AI service instance

        Raises:
            ValueError: If provider is not supported or not configured
        """
        if provider == "gemini":
            return self._create_gemini_service()
        elif provider == "openai":
            return self._create_openai_service()
        elif provider == "claude":
            return self._create_claude_service()
        elif provider == "deepseek":
            return self._create_deepseek_service()
        else:
            raise ValueError(f"Unsupported AI provider: {provider}")

    def _create_gemini_service(self) -> AIServiceBase:
        """Create Gemini AI service instance."""
        from backend.app.services.gemini_service import GeminiService

        if not settings.GEMINI_API_KEY:
            raise ValueError("Gemini API key not configured")

        return GeminiService()

    def _create_openai_service(self) -> AIServiceBase:
        """Create OpenAI service instance."""
        from backend.app.services.openai_service import OpenAIService

        openai_key = getattr(settings, 'OPENAI_API_KEY', None)
        if not openai_key:
            raise ValueError("OpenAI API key not configured")

        # Updated to latest GPT-5.2 model
        model = getattr(settings, 'OPENAI_MODEL', 'gpt-5.2-chat-latest')
        return OpenAIService(model_name=model, api_key=openai_key)

    def _create_claude_service(self) -> AIServiceBase:
        """Create Claude service instance."""
        from backend.app.services.claude_service import ClaudeService

        claude_key = getattr(settings, 'CLAUDE_API_KEY', None)
        if not claude_key:
            raise ValueError("Claude API key not configured")

        # Updated to latest Claude Opus 4.5 model
        model = getattr(settings, 'CLAUDE_MODEL', 'claude-opus-4.5-20251101')
        return ClaudeService(model_name=model, api_key=claude_key)

    def _create_deepseek_service(self) -> AIServiceBase:
        """Create DeepSeek service instance."""
        from backend.app.services.deepseek_service import DeepSeekService

        deepseek_key = getattr(settings, 'DEEPSEEK_API_KEY', None)
        if not deepseek_key:
            raise ValueError("DeepSeek API key not configured")

        # Updated to latest DeepSeek V3.2 with reasoning (思考推理模式)
        model = getattr(settings, 'DEEPSEEK_MODEL', 'deepseek-reasoner')
        return DeepSeekService(model_name=model, api_key=deepseek_key)

    def set_provider(self, provider: AIProvider) -> None:
        """
        Set the current AI provider.

        Args:
            provider: AI provider name

        Raises:
            ValueError: If provider is not supported
        """
        if provider not in ["gemini", "openai", "claude", "deepseek"]:
            raise ValueError(f"Unsupported AI provider: {provider}")

        self._current_provider = provider
        logger.info(f"Switched AI provider to: {provider}")

    def get_current_provider(self) -> AIProvider:
        """Get the current AI provider name."""
        return self._current_provider

    def get_available_providers(self) -> Dict[str, Dict[str, any]]:
        """
        Get information about available AI providers.

        Returns:
            Dictionary mapping provider names to their status and model info
        """
        providers = {}

        # Check Gemini
        providers["gemini"] = {
            "available": bool(settings.GEMINI_API_KEY),
            "model": settings.GEMINI_MODEL if hasattr(settings, 'GEMINI_MODEL') else None,
            "supports_streaming": True,
            "supports_images": True,
        }

        # Check OpenAI
        openai_key = getattr(settings, 'OPENAI_API_KEY', None)
        providers["openai"] = {
            "available": bool(openai_key),
            "model": getattr(settings, 'OPENAI_MODEL', 'gpt-5.2-chat-latest'),
            "supports_streaming": True,
            "supports_images": True,
        }

        # Check Claude
        claude_key = getattr(settings, 'CLAUDE_API_KEY', None)
        providers["claude"] = {
            "available": bool(claude_key),
            "model": getattr(settings, 'CLAUDE_MODEL', 'claude-opus-4.5-20251101'),
            "supports_streaming": True,
            "supports_images": True,
        }

        # Check DeepSeek
        deepseek_key = getattr(settings, 'DEEPSEEK_API_KEY', None)
        providers["deepseek"] = {
            "available": bool(deepseek_key),
            "model": getattr(settings, 'DEEPSEEK_MODEL', 'deepseek-reasoner'),
            "supports_streaming": True,
            "supports_images": False,
        }

        return providers

    def get_usage_summary(self) -> Dict[str, any]:
        """
        Get usage summary across all providers.

        Returns:
            Dictionary with usage statistics
        """
        summary = {
            "total_cost": 0.0,
            "total_tokens": 0,
            "by_provider": {}
        }

        for provider_name, service in self._services.items():
            cost = service.get_total_cost()
            tokens = service.get_total_tokens()

            summary["total_cost"] += cost
            summary["total_tokens"] += tokens
            summary["by_provider"][provider_name] = {
                "cost": cost,
                "tokens": tokens,
                "model": service.model_name,
            }

        return summary

    def clear_cache(self) -> None:
        """Clear all cached service instances."""
        self._services.clear()
        logger.info("Cleared AI service cache")


# Global factory instance
ai_factory = AIServiceFactory()


def get_ai_service(provider: Optional[AIProvider] = None) -> AIServiceBase:
    """
    Convenience function to get AI service instance.

    Args:
        provider: Optional AI provider name

    Returns:
        AI service instance
    """
    return ai_factory.get_service(provider)
