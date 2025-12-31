"""
API endpoints for AI model management and cost tracking.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Literal
from backend.app.services.ai_service_factory import ai_factory

router = APIRouter()

AIProvider = Literal["gemini", "openai", "claude"]


class ModelSelectionRequest(BaseModel):
    """Request to select AI provider."""
    provider: AIProvider


class ModelSelectionResponse(BaseModel):
    """Response after selecting AI provider."""
    provider: AIProvider
    model_name: str
    success: bool
    message: str


class ProviderInfo(BaseModel):
    """Information about an AI provider."""
    name: str
    available: bool
    model: str
    supports_streaming: bool
    supports_images: bool
    current: bool


class ProvidersListResponse(BaseModel):
    """List of available AI providers."""
    providers: List[ProviderInfo]
    current_provider: str


class UsageStatsResponse(BaseModel):
    """API usage statistics."""
    total_cost: float
    total_tokens: int
    by_provider: Dict[str, Dict[str, Any]]


@router.get("/providers", response_model=ProvidersListResponse)
async def list_providers():
    """
    List all available AI providers and their status.

    Returns information about Gemini, OpenAI, and Claude,
    including whether they're configured and available.
    """
    try:
        providers_info = ai_factory.get_available_providers()
        current = ai_factory.get_current_provider()

        providers_list = []
        for name, info in providers_info.items():
            providers_list.append(
                ProviderInfo(
                    name=name,
                    available=info["available"],
                    model=info["model"] or "N/A",
                    supports_streaming=info["supports_streaming"],
                    supports_images=info["supports_images"],
                    current=(name == current),
                )
            )

        return ProvidersListResponse(
            providers=providers_list,
            current_provider=current,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list providers: {str(e)}")


@router.post("/provider/select", response_model=ModelSelectionResponse)
async def select_provider(request: ModelSelectionRequest):
    """
    Select and switch to a different AI provider.

    Args:
        request: Provider selection request

    Returns:
        Selection result with provider info
    """
    try:
        # Check if provider is available
        providers = ai_factory.get_available_providers()

        if request.provider not in providers:
            raise HTTPException(
                status_code=400,
                detail=f"Provider '{request.provider}' is not supported"
            )

        if not providers[request.provider]["available"]:
            raise HTTPException(
                status_code=400,
                detail=f"Provider '{request.provider}' is not configured. Please add API key to .env file."
            )

        # Switch provider
        ai_factory.set_provider(request.provider)

        # Get service to retrieve model name
        service = ai_factory.get_service(request.provider)

        return ModelSelectionResponse(
            provider=request.provider,
            model_name=service.model_name,
            success=True,
            message=f"Successfully switched to {request.provider} ({service.model_name})"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to switch provider: {str(e)}")


@router.get("/provider/current")
async def get_current_provider():
    """
    Get the currently active AI provider.

    Returns:
        Current provider name and model
    """
    try:
        current = ai_factory.get_current_provider()
        service = ai_factory.get_service(current)

        return {
            "provider": current,
            "model_name": service.model_name,
            "provider_name": service.provider_name,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get current provider: {str(e)}")


@router.get("/usage/stats", response_model=UsageStatsResponse)
async def get_usage_stats():
    """
    Get API usage statistics across all providers.

    Returns:
        Total cost, total tokens, and breakdown by provider
    """
    try:
        summary = ai_factory.get_usage_summary()
        return UsageStatsResponse(**summary)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get usage stats: {str(e)}")


@router.post("/usage/clear")
async def clear_usage_stats():
    """
    Clear all cached usage statistics.

    This will reset the cost tracking but won't affect
    the service instances or provider selection.
    """
    try:
        ai_factory.clear_cache()
        return {
            "success": True,
            "message": "Usage statistics cleared successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear stats: {str(e)}")


@router.get("/models/compare")
async def compare_models():
    """
    Compare available AI models by features and pricing.

    Returns:
        Comparison table of all available models
    """
    return {
        "models": [
            {
                "provider": "gemini",
                "model": "gemini-3-flash-preview",
                "strengths": ["Fast", "Multimodal", "Free tier available", "Good for Chinese"],
                "cost_per_1k_tokens": {"input": 0.0, "output": 0.0},  # Free tier
                "max_tokens": 32000,
                "supports_images": True,
                "supports_streaming": True,
            },
            {
                "provider": "openai",
                "model": "gpt-4-turbo-preview",
                "strengths": ["High quality", "Latest features", "Reliable"],
                "cost_per_1k_tokens": {"input": 0.01, "output": 0.03},
                "max_tokens": 128000,
                "supports_images": True,
                "supports_streaming": True,
            },
            {
                "provider": "claude",
                "model": "claude-3-5-sonnet-20241022",
                "strengths": ["Excellent reasoning", "Long context", "Good at coding"],
                "cost_per_1k_tokens": {"input": 0.003, "output": 0.015},
                "max_tokens": 200000,
                "supports_images": True,
                "supports_streaming": True,
            },
        ],
        "recommendation": {
            "for_cost": "gemini",
            "for_quality": "claude",
            "for_speed": "gemini",
            "for_chinese": "gemini",
        }
    }
