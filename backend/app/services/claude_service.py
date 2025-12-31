"""
Claude API service for AI operations.
"""
import anthropic
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


class ClaudeService(AIServiceBase):
    """Service for interacting with Anthropic Claude API."""

    def __init__(self, model_name: str, api_key: str):
        """
        Initialize Claude service.

        Args:
            model_name: Claude model name (e.g., "claude-3-5-sonnet-20241022")
            api_key: Anthropic API key
        """
        super().__init__(model_name, api_key)
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        logger.info(f"Initialized Claude service with model: {model_name}")

    @property
    def provider_name(self) -> str:
        return "Claude"

    @property
    def supports_streaming(self) -> bool:
        return True

    @property
    def supports_images(self) -> bool:
        return True  # Claude 3 支持图像

    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate text using Claude API."""
        try:
            kwargs = {
                "model": self.model_name,
                "max_tokens": max_tokens or 4096,
                "temperature": temperature,
                "messages": [{"role": "user", "content": prompt}],
            }

            if system_instruction:
                kwargs["system"] = system_instruction

            response = await self.client.messages.create(**kwargs)

            # Record usage
            usage = response.usage
            if usage:
                cost = self.estimate_cost(usage.input_tokens, usage.output_tokens)
                stats = AIUsageStats(
                    model_name=self.model_name,
                    prompt_tokens=usage.input_tokens,
                    completion_tokens=usage.output_tokens,
                    total_tokens=usage.input_tokens + usage.output_tokens,
                    estimated_cost=cost,
                    timestamp=datetime.now(timezone.utc),
                )
                self.record_usage(stats)

            return response.content[0].text

        except Exception as e:
            logger.error(f"Error generating text with Claude: {str(e)}")
            raise

    async def chat(
        self,
        messages: List[AIMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Chat with conversation history."""
        try:
            # Convert AIMessage to Claude format
            claude_messages = []
            system_message = None

            for msg in messages:
                if msg.role == "system":
                    system_message = msg.content
                    continue

                content = msg.content
                if msg.images and self.supports_images:
                    # For vision support, include images
                    content = [{"type": "text", "text": msg.content}]
                    for img_path in msg.images:
                        import base64
                        with open(img_path, "rb") as image_file:
                            image_data = base64.b64encode(image_file.read()).decode('utf-8')

                        # Detect image type
                        ext = img_path.lower().split('.')[-1]
                        media_type = f"image/{ext}" if ext in ["jpeg", "png", "gif", "webp"] else "image/jpeg"

                        content.append({
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            }
                        })

                claude_messages.append({
                    "role": msg.role if msg.role in ["user", "assistant"] else "user",
                    "content": content
                })

            kwargs = {
                "model": self.model_name,
                "max_tokens": max_tokens or 4096,
                "temperature": temperature,
                "messages": claude_messages,
            }

            if system_message:
                kwargs["system"] = system_message

            response = await self.client.messages.create(**kwargs)

            # Record usage
            usage = response.usage
            if usage:
                cost = self.estimate_cost(usage.input_tokens, usage.output_tokens)
                stats = AIUsageStats(
                    model_name=self.model_name,
                    prompt_tokens=usage.input_tokens,
                    completion_tokens=usage.output_tokens,
                    total_tokens=usage.input_tokens + usage.output_tokens,
                    estimated_cost=cost,
                    timestamp=datetime.now(timezone.utc),
                )
                self.record_usage(stats)

            return response.content[0].text

        except Exception as e:
            logger.error(f"Error in Claude chat: {str(e)}")
            raise

    async def chat_stream(
        self,
        messages: List[AIMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> AsyncGenerator[str, None]:
        """Chat with streaming response."""
        try:
            claude_messages = []
            system_message = None

            for msg in messages:
                if msg.role == "system":
                    system_message = msg.content
                    continue
                claude_messages.append({
                    "role": msg.role if msg.role in ["user", "assistant"] else "user",
                    "content": msg.content
                })

            kwargs = {
                "model": self.model_name,
                "max_tokens": max_tokens or 4096,
                "temperature": temperature,
                "messages": claude_messages,
            }

            if system_message:
                kwargs["system"] = system_message

            async with self.client.messages.stream(**kwargs) as stream:
                async for text in stream.text_stream:
                    yield text

        except Exception as e:
            logger.error(f"Error in Claude streaming chat: {str(e)}")
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
        default_prompt = """
请分析这张图片，提取以下信息并以JSON格式返回：
1. UI布局（layout）
2. 颜色方案（colors）
3. 组件列表（components）
4. 页面结构（page_structure）
"""

        analysis_prompt = prompt or default_prompt

        messages = [AIMessage(
            role="user",
            content=analysis_prompt,
            images=[image_path]
        )]

        response = await self.chat(messages, temperature=0.3)

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
            return {"description": response}

    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """
        Estimate cost for Claude API usage.

        Pricing (as of Dec 2025):
        - Claude 3.5 Sonnet: $0.003/1K input, $0.015/1K output
        - Claude 3 Opus: $0.015/1K input, $0.075/1K output
        - Claude 3 Haiku: $0.00025/1K input, $0.00125/1K output
        """
        model_lower = self.model_name.lower()

        if "sonnet" in model_lower:
            prompt_cost = (prompt_tokens / 1000) * 0.003
            completion_cost = (completion_tokens / 1000) * 0.015
        elif "opus" in model_lower:
            prompt_cost = (prompt_tokens / 1000) * 0.015
            completion_cost = (completion_tokens / 1000) * 0.075
        elif "haiku" in model_lower:
            prompt_cost = (prompt_tokens / 1000) * 0.00025
            completion_cost = (completion_tokens / 1000) * 0.00125
        else:  # Default to Sonnet pricing
            prompt_cost = (prompt_tokens / 1000) * 0.003
            completion_cost = (completion_tokens / 1000) * 0.015

        return prompt_cost + completion_cost
