"""
DeepSeek API service for AI operations.
"""
import openai
from backend.app.services.ai_service_base import (
    AIServiceBase,
    AIMessage,
    AIUsageStats
)
from typing import Optional, List, Dict, Any, AsyncGenerator
from datetime import datetime, timezone
import logging
import json

logger = logging.getLogger(__name__)


class DeepSeekService(AIServiceBase):
    """Service for interacting with DeepSeek API (DeepSeek-V3, etc.)."""

    def __init__(self, model_name: str, api_key: str):
        """
        Initialize DeepSeek service.

        Args:
            model_name: DeepSeek model name (e.g., "deepseek-chat")
            api_key: DeepSeek API key
        """
        super().__init__(model_name, api_key)
        # DeepSeek uses OpenAI-compatible API
        self.client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        logger.info(f"Initialized DeepSeek service with model: {model_name}")

    @property
    def provider_name(self) -> str:
        return "DeepSeek"

    @property
    def supports_streaming(self) -> bool:
        return True

    @property
    def supports_images(self) -> bool:
        # DeepSeek currently doesn't support image analysis
        return False

    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate text using DeepSeek API."""
        try:
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            messages.append({"role": "user", "content": prompt})

            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            # Record usage
            usage = response.usage
            if usage:
                cost = self.estimate_cost(usage.prompt_tokens, usage.completion_tokens)
                stats = AIUsageStats(
                    model_name=self.model_name,
                    prompt_tokens=usage.prompt_tokens,
                    completion_tokens=usage.completion_tokens,
                    total_tokens=usage.total_tokens,
                    estimated_cost=cost,
                    timestamp=datetime.now(timezone.utc),
                )
                self.record_usage(stats)

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error generating text with DeepSeek: {str(e)}")
            raise

    async def chat(
        self,
        messages: List[AIMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Chat with conversation history."""
        try:
            deepseek_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]

            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=deepseek_messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            # Record usage
            usage = response.usage
            if usage:
                cost = self.estimate_cost(usage.prompt_tokens, usage.completion_tokens)
                stats = AIUsageStats(
                    model_name=self.model_name,
                    prompt_tokens=usage.prompt_tokens,
                    completion_tokens=usage.completion_tokens,
                    total_tokens=usage.total_tokens,
                    estimated_cost=cost,
                    timestamp=datetime.now(timezone.utc),
                )
                self.record_usage(stats)

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error in DeepSeek chat: {str(e)}")
            raise

    async def chat_stream(
        self,
        messages: List[AIMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> AsyncGenerator[str, None]:
        """Chat with streaming response."""
        try:
            deepseek_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]

            stream = await self.client.chat.completions.create(
                model=self.model_name,
                messages=deepseek_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"Error in DeepSeek streaming chat: {str(e)}")
            raise

    async def analyze_document(
        self,
        document_content: str,
        document_type: str,
        filename: str = "",
    ) -> Dict[str, Any]:
        """Analyze a document and extract structured information."""
        prompt = f"""
请分析以下文档（文件名：{filename}），提取关键信息：

文档类型：{document_type}
文档内容：
{document_content[:8000]}

请以JSON格式返回分析结果，包括：
1. 文档概述（summary）
2. 关键实体（entities）
3. UI信息（ui_info）
4. 技术约定（tech_info）
5. 重要引用（references）
"""

        response = await self.generate_text(
            prompt=prompt,
            system_instruction="你是一个专业的产品需求分析助手。请返回有效的JSON格式。",
            temperature=0.3,
        )

        try:
            clean_response = response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.startswith("```"):
                clean_response = clean_response[3:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]

            return json.loads(clean_response.strip())
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON response")
            return {
                "summary": response[:500],
                "entities": [],
                "ui_info": {},
                "tech_info": {},
                "references": []
            }

    async def analyze_image(
        self,
        image_path: str,
        prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Analyze an image and extract information."""
        raise NotImplementedError("DeepSeek does not support image analysis yet")

    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """
        Estimate cost for DeepSeek API usage.

        Pricing (as of Dec 2025):
        - DeepSeek-Chat: ¥0.001/1K tokens input, ¥0.002/1K tokens output
        - DeepSeek-Coder: Similar pricing

        Using approximate USD conversion: ¥1 ≈ $0.14
        """
        # DeepSeek pricing in CNY per 1K tokens
        prompt_cost_cny = (prompt_tokens / 1000) * 0.001
        completion_cost_cny = (completion_tokens / 1000) * 0.002

        # Convert to USD (approximate)
        total_cost_usd = (prompt_cost_cny + completion_cost_cny) * 0.14

        return total_cost_usd
