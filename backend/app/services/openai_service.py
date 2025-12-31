"""
OpenAI API service for AI operations.
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


class OpenAIService(AIServiceBase):
    """Service for interacting with OpenAI API (GPT-4, GPT-4-turbo, etc.)."""

    def __init__(self, model_name: str, api_key: str):
        """
        Initialize OpenAI service.

        Args:
            model_name: OpenAI model name (e.g., "gpt-4-turbo-preview")
            api_key: OpenAI API key
        """
        super().__init__(model_name, api_key)
        self.client = openai.AsyncOpenAI(api_key=api_key)
        logger.info(f"Initialized OpenAI service with model: {model_name}")

    @property
    def provider_name(self) -> str:
        return "OpenAI"

    @property
    def supports_streaming(self) -> bool:
        return True

    @property
    def supports_images(self) -> bool:
        return "vision" in self.model_name.lower() or "gpt-4" in self.model_name.lower()

    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate text using OpenAI API."""
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
            logger.error(f"Error generating text with OpenAI: {str(e)}")
            raise

    async def chat(
        self,
        messages: List[AIMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Chat with conversation history."""
        try:
            openai_messages = []
            for msg in messages:
                content = msg.content
                if msg.images and self.supports_images:
                    # For vision models, include images
                    content = [{"type": "text", "text": msg.content}]
                    for img_path in msg.images:
                        content.append({
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{self._encode_image(img_path)}"}
                        })

                openai_messages.append({
                    "role": msg.role if msg.role != "assistant" else "assistant",
                    "content": content
                })

            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=openai_messages,
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
            logger.error(f"Error in OpenAI chat: {str(e)}")
            raise

    async def chat_stream(
        self,
        messages: List[AIMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> AsyncGenerator[str, None]:
        """Chat with streaming response."""
        try:
            openai_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]

            stream = await self.client.chat.completions.create(
                model=self.model_name,
                messages=openai_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"Error in OpenAI streaming chat: {str(e)}")
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
        if not self.supports_images:
            raise NotImplementedError(f"Model {self.model_name} does not support image analysis")

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
        Estimate cost for OpenAI API usage.

        Pricing (as of Dec 2025):
        - GPT-4-turbo: $0.01/1K prompt, $0.03/1K completion
        - GPT-4: $0.03/1K prompt, $0.06/1K completion
        """
        if "gpt-4-turbo" in self.model_name.lower():
            prompt_cost = (prompt_tokens / 1000) * 0.01
            completion_cost = (completion_tokens / 1000) * 0.03
        elif "gpt-4" in self.model_name.lower():
            prompt_cost = (prompt_tokens / 1000) * 0.03
            completion_cost = (completion_tokens / 1000) * 0.06
        else:  # GPT-3.5-turbo or other
            prompt_cost = (prompt_tokens / 1000) * 0.0015
            completion_cost = (completion_tokens / 1000) * 0.002

        return prompt_cost + completion_cost

    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64."""
        import base64
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
