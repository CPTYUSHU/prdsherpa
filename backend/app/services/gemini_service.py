"""
Gemini API service for AI operations.
"""
import google.generativeai as genai
from backend.app.core.config import settings
from typing import Optional, List, Dict, Any
import logging
import os

logger = logging.getLogger(__name__)

# Configure proxy if available
if hasattr(settings, 'HTTP_PROXY') and settings.HTTP_PROXY:
    os.environ['HTTP_PROXY'] = settings.HTTP_PROXY
    os.environ['HTTPS_PROXY'] = settings.HTTP_PROXY
    logger.info(f"Using proxy: {settings.HTTP_PROXY}")

# Configure Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)


class GeminiService:
    """Service for interacting with Gemini API."""
    
    def __init__(self):
        self.model_name = settings.GEMINI_MODEL
        self.model = genai.GenerativeModel(self.model_name)
        logger.info(f"Initialized Gemini service with model: {self.model_name}")
    
    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate text using Gemini API.
        
        Args:
            prompt: User prompt
            system_instruction: System instruction for the model
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
        
        Returns:
            Generated text
        """
        try:
            # Prepare generation config
            generation_config = {
                "temperature": temperature,
            }
            if max_tokens:
                generation_config["max_output_tokens"] = max_tokens
            
            # Create model with system instruction if provided
            if system_instruction:
                model = genai.GenerativeModel(
                    self.model_name,
                    system_instruction=system_instruction,
                    generation_config=generation_config,
                )
            else:
                model = genai.GenerativeModel(
                    self.model_name,
                    generation_config=generation_config,
                )
            
            # Generate content
            response = model.generate_content(prompt)
            
            logger.info(f"Generated text with {len(response.text)} characters")
            return response.text
        
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            raise
    
    async def analyze_document_with_images(
        self,
        document_content: str,
        document_type: str,
        filename: str = "",
        image_paths: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze a document with optional images and extract structured information.

        Args:
            document_content: Document text content
            document_type: Type of document (e.g., "prd", "pptx", "pdf")
            filename: Original filename
            image_paths: Optional list of image file paths from document

        Returns:
            Structured analysis result
        """
        prompt = f"""
请分析以下文档（文件名：{filename}），提取关键信息：

文档类型：{document_type}

文档内容：
{document_content[:5000]}

{"另外，文档中包含 " + str(len(image_paths)) + " 张图片，请仔细分析这些图片中的UI设计、流程图、架构图等信息，提取其中的关键要素。" if image_paths else ""}

请以JSON格式返回分析结果，包括：
1. 文档概述（summary）：简要描述文档的主要内容
2. 关键实体（entities）：识别到的模块名、功能名、字段名、API 名称等
3. UI信息（ui_info）：如果有UI相关描述或图片，提取布局、颜色、组件、页面结构等信息
4. 技术约定（tech_info）：字段命名规范、API风格、数据类型、架构模式等
5. 重要引用（references）：值得记录的具体内容片段

返回格式示例：
{{
  "summary": "这是一个用户管理模块的PRD文档，包含登录、注册等功能...",
  "entities": ["用户管理", "userID", "登录接口", "首页"],
  "ui_info": {{"layout": "底部Tab导航", "colors": ["#4299E1", "#F6AD55"], "pages": ["首页", "我的"]}},
  "tech_info": {{"naming": "camelCase", "api_style": "RESTful"}},
  "references": ["用户ID使用userID字段", "主色调使用蓝色#4299E1"]
}}
"""

        try:
            if image_paths and len(image_paths) > 0:
                # Upload images and create multimodal request
                parts = [prompt]
                for img_path in image_paths[:10]:  # Limit to 10 images
                    try:
                        uploaded_file = genai.upload_file(img_path)
                        parts.append(uploaded_file)
                        logger.info(f"Added image to document analysis: {img_path}")
                    except Exception as img_error:
                        logger.warning(f"Failed to upload image {img_path}: {img_error}")

                response = self.model.generate_content(parts)
                response_text = response.text
            else:
                response_text = await self.generate_text(
                    prompt=prompt,
                    system_instruction="你是一个专业的产品需求分析助手，擅长从文档中提取结构化信息。请始终返回有效的JSON格式。",
                    temperature=0.3,
                )

            # Parse JSON response
            try:
                import json
                clean_response = response_text.strip()
                if clean_response.startswith("```json"):
                    clean_response = clean_response[7:]
                if clean_response.startswith("```"):
                    clean_response = clean_response[3:]
                if clean_response.endswith("```"):
                    clean_response = clean_response[:-3]

                analysis = json.loads(clean_response.strip())
                return analysis
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON response from document with images")
                return {
                    "summary": response_text[:500],
                    "entities": [],
                    "ui_info": {},
                    "tech_info": {},
                    "references": []
                }

        except Exception as e:
            logger.error(f"Error analyzing document with images: {str(e)}")
            raise

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
            document_type: Type of document (e.g., "prd", "api_doc", "text")
            filename: Original filename

        Returns:
            Structured analysis result
        """
        prompt = f"""
请分析以下文档（文件名：{filename}），提取关键信息：

文档类型：{document_type}

文档内容：
{document_content[:5000]}  # 限制长度避免超出 token 限制

请以JSON格式返回分析结果，包括：
1. 文档概述（summary）：简要描述文档的主要内容
2. 关键实体（entities）：识别到的模块名、功能名、字段名、API 名称等
3. UI信息（ui_info）：如果有UI相关描述，提取布局、颜色、组件等信息
4. 技术约定（tech_info）：字段命名规范、API风格、数据类型等
5. 重要引用（references）：值得记录的具体内容片段

返回格式示例：
{{
  "summary": "这是一个用户管理模块的PRD文档...",
  "entities": ["用户管理", "userID", "登录接口"],
  "ui_info": {{"layout": "左侧导航", "colors": ["#4299E1"]}},
  "tech_info": {{"naming": "camelCase", "api_style": "RESTful"}},
  "references": ["用户ID使用userID字段"]
}}
"""
        
        try:
            response = await self.generate_text(
                prompt=prompt,
                system_instruction="你是一个专业的产品需求分析助手，擅长从文档中提取结构化信息。请始终返回有效的JSON格式。",
                temperature=0.3,  # Lower temperature for more consistent extraction
            )
            
            # Try to parse JSON, if fails, return raw text
            try:
                import json
                # Remove markdown code blocks if present
                clean_response = response.strip()
                if clean_response.startswith("```json"):
                    clean_response = clean_response[7:]
                if clean_response.startswith("```"):
                    clean_response = clean_response[3:]
                if clean_response.endswith("```"):
                    clean_response = clean_response[:-3]
                
                analysis = json.loads(clean_response.strip())
                return analysis
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON response, returning raw text")
                return {
                    "summary": response,
                    "entities": [],
                    "ui_info": {},
                    "tech_info": {},
                    "references": []
                }
        
        except Exception as e:
            logger.error(f"Error analyzing document: {str(e)}")
            raise
    
    async def analyze_image(
        self,
        image_path: str,
    ) -> Dict[str, Any]:
        """
        Analyze an image (screenshot) and extract UI information.
        
        Args:
            image_path: Path to the image file
        
        Returns:
            Structured analysis result
        """
        try:
            # Upload image
            image_file = genai.upload_file(image_path)
            
            prompt = """
请分析这张UI截图，提取以下信息：
1. 页面类型（如：列表页、详情页、表单页等）
2. 主要UI组件（按钮、表格、表单等）
3. 色彩方案（主色调、辅助色）
4. 布局特征（导航位置、内容区域划分等）
5. 可见的文字内容和标签

请以JSON格式返回分析结果。
"""
            
            response = self.model.generate_content([prompt, image_file])
            
            logger.info(f"Analyzed image: {image_path}")
            
            # TODO: Parse JSON response
            return {"raw_analysis": response.text}
        
        except Exception as e:
            logger.error(f"Error analyzing image: {str(e)}")
            raise
    
    async def chat(
        self,
        messages: List[Dict[str, Any]],
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        image_paths: Optional[List[str]] = None,
    ) -> str:
        """
        Chat with Gemini using conversation history, with optional image support.
        
        Args:
            messages: List of messages [{"role": "user", "content": "..."}, ...]
            system_instruction: System instruction
            temperature: Sampling temperature
            image_paths: Optional list of image file paths to include in the last message
        
        Returns:
            Assistant's response
        """
        try:
            # Create chat session
            if system_instruction:
                model = genai.GenerativeModel(
                    self.model_name,
                    system_instruction=system_instruction,
                )
            else:
                model = self.model
            
            chat = model.start_chat(history=[])
            
            # Add history (all messages except the last one)
            for msg in messages[:-1]:
                role = "user" if msg["role"] == "user" else "model"
                chat.history.append({
                    "role": role,
                    "parts": [msg["content"]],
                })
            
            # Prepare the last message with optional images
            last_message_content = messages[-1]["content"]
            
            if image_paths and len(image_paths) > 0:
                # Upload images and create multimodal message
                parts = []
                
                # Add images first
                for img_path in image_paths:
                    try:
                        uploaded_file = genai.upload_file(img_path)
                        parts.append(uploaded_file)
                        logger.info(f"Uploaded image: {img_path}")
                    except Exception as img_error:
                        logger.error(f"Failed to upload image {img_path}: {img_error}")
                
                # Add text
                parts.append(last_message_content)
                
                # Send multimodal message
                response = chat.send_message(parts)
            else:
                # Send text-only message
                response = chat.send_message(last_message_content)
            
            logger.info(f"Chat response generated with {len(response.text)} characters")
            return response.text

        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            raise

    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        image_paths: Optional[List[str]] = None,
    ):
        """
        Chat with Gemini using conversation history with streaming response.

        Args:
            messages: List of messages [{"role": "user", "content": "..."}, ...]
            system_instruction: System instruction
            temperature: Sampling temperature
            image_paths: Optional list of image file paths to include in the last message

        Yields:
            Text chunks as they are generated
        """
        try:
            # Create chat session
            if system_instruction:
                model = genai.GenerativeModel(
                    self.model_name,
                    system_instruction=system_instruction,
                )
            else:
                model = self.model

            chat = model.start_chat(history=[])

            # Add history (all messages except the last one)
            for msg in messages[:-1]:
                role = "user" if msg["role"] == "user" else "model"
                chat.history.append({
                    "role": role,
                    "parts": [msg["content"]],
                })

            # Prepare the last message with optional images
            last_message_content = messages[-1]["content"]

            if image_paths and len(image_paths) > 0:
                # Upload images and create multimodal message
                parts = []

                # Add images first
                for img_path in image_paths:
                    try:
                        uploaded_file = genai.upload_file(img_path)
                        parts.append(uploaded_file)
                        logger.info(f"Uploaded image: {img_path}")
                    except Exception as img_error:
                        logger.error(f"Failed to upload image {img_path}: {img_error}")

                # Add text
                parts.append(last_message_content)

                # Send multimodal message with streaming
                response = chat.send_message(parts, stream=True)
            else:
                # Send text-only message with streaming
                response = chat.send_message(last_message_content, stream=True)

            # Yield chunks as they arrive
            for chunk in response:
                if chunk.text:
                    yield chunk.text

            logger.info("Chat streaming completed")

        except Exception as e:
            logger.error(f"Error in chat stream: {str(e)}")
            raise


# Global instance
gemini_service = GeminiService()

