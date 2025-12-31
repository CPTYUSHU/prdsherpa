"""
AI API Testing endpoint - Test API keys validity
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai", tags=["AI Testing"])


class APITestRequest(BaseModel):
    provider: Literal["gemini", "openai", "claude", "deepseek"]
    api_key: str


class APITestResponse(BaseModel):
    success: bool
    message: str
    model_name: str = ""
    error: str = ""


@router.post("/test", response_model=APITestResponse)
async def test_api_key(request: APITestRequest):
    """
    Test if an API key is valid by making a simple API call.

    Args:
        request: Provider name and API key

    Returns:
        Test result with success status and message
    """
    try:
        if request.provider == "gemini":
            return await _test_gemini(request.api_key)
        elif request.provider == "openai":
            return await _test_openai(request.api_key)
        elif request.provider == "claude":
            return await _test_claude(request.api_key)
        elif request.provider == "deepseek":
            return await _test_deepseek(request.api_key)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {request.provider}")

    except Exception as e:
        logger.error(f"API test failed for {request.provider}: {str(e)}")
        return APITestResponse(
            success=False,
            message="API Key 测试失败",
            error=str(e)
        )


async def _test_gemini(api_key: str) -> APITestResponse:
    """Test Google Gemini API key"""
    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')

        # Simple test prompt
        response = model.generate_content("Say 'Hello'")

        if response and response.text:
            return APITestResponse(
                success=True,
                message="Gemini API Key 有效",
                model_name="gemini-2.0-flash-exp"
            )
        else:
            return APITestResponse(
                success=False,
                message="API 返回异常",
                error="No response from API"
            )

    except Exception as e:
        error_msg = str(e)
        if "API_KEY_INVALID" in error_msg or "invalid" in error_msg.lower():
            return APITestResponse(
                success=False,
                message="API Key 无效",
                error="无效的 API Key"
            )
        else:
            return APITestResponse(
                success=False,
                message="连接失败",
                error=error_msg
            )


async def _test_openai(api_key: str) -> APITestResponse:
    """Test OpenAI API key"""
    try:
        import openai

        client = openai.AsyncOpenAI(api_key=api_key)

        # Simple test prompt using latest model
        response = await client.chat.completions.create(
            model="gpt-5.2-chat-latest",
            messages=[{"role": "user", "content": "Say 'Hello'"}],
            max_tokens=10
        )

        if response and response.choices:
            return APITestResponse(
                success=True,
                message="OpenAI API Key 有效",
                model_name="gpt-5.2-chat-latest"
            )
        else:
            return APITestResponse(
                success=False,
                message="API 返回异常",
                error="No response from API"
            )

    except Exception as e:
        error_msg = str(e)
        if "invalid" in error_msg.lower() or "unauthorized" in error_msg.lower():
            return APITestResponse(
                success=False,
                message="API Key 无效",
                error="无效的 API Key 或权限不足"
            )
        else:
            return APITestResponse(
                success=False,
                message="连接失败",
                error=error_msg
            )


async def _test_claude(api_key: str) -> APITestResponse:
    """Test Anthropic Claude API key"""
    try:
        import anthropic

        client = anthropic.AsyncAnthropic(api_key=api_key)

        # Simple test prompt using latest model
        response = await client.messages.create(
            model="claude-opus-4.5-20251101",
            max_tokens=10,
            messages=[{"role": "user", "content": "Say 'Hello'"}]
        )

        if response and response.content:
            return APITestResponse(
                success=True,
                message="Claude API Key 有效",
                model_name="claude-opus-4.5-20251101"
            )
        else:
            return APITestResponse(
                success=False,
                message="API 返回异常",
                error="No response from API"
            )

    except Exception as e:
        error_msg = str(e)
        if "invalid" in error_msg.lower() or "unauthorized" in error_msg.lower():
            return APITestResponse(
                success=False,
                message="API Key 无效",
                error="无效的 API Key 或权限不足"
            )
        else:
            return APITestResponse(
                success=False,
                message="连接失败",
                error=error_msg
            )


async def _test_deepseek(api_key: str) -> APITestResponse:
    """Test DeepSeek API key"""
    try:
        import openai

        # DeepSeek uses OpenAI-compatible API
        client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )

        # Simple test prompt using latest model with reasoning
        response = await client.chat.completions.create(
            model="deepseek-reasoner",
            messages=[{"role": "user", "content": "Say 'Hello'"}],
            max_tokens=10
        )

        if response and response.choices:
            return APITestResponse(
                success=True,
                message="DeepSeek API Key 有效",
                model_name="deepseek-reasoner (V3.2)"
            )
        else:
            return APITestResponse(
                success=False,
                message="API 返回异常",
                error="No response from API"
            )

    except Exception as e:
        error_msg = str(e)
        if "invalid" in error_msg.lower() or "unauthorized" in error_msg.lower():
            return APITestResponse(
                success=False,
                message="API Key 无效",
                error="无效的 API Key 或权限不足"
            )
        else:
            return APITestResponse(
                success=False,
                message="连接失败",
                error=error_msg
            )
