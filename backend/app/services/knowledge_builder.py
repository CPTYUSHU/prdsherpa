"""
Knowledge base building service.
Integrates all file analysis results into a structured knowledge base.
"""
import logging
import json
from typing import List, Dict, Any
from backend.app.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)


class KnowledgeBuilder:
    """Service for building project knowledge base from file analyses."""
    
    async def build_knowledge_base(
        self,
        project_name: str,
        file_analyses: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Build a structured knowledge base from multiple file analyses.
        
        Args:
            project_name: Name of the project
            file_analyses: List of file analysis results
        
        Returns:
            Structured knowledge base
        """
        logger.info(f"Building knowledge base for project: {project_name}")
        logger.info(f"Processing {len(file_analyses)} file analyses")
        
        # Prepare context from all files
        context = self._prepare_context(project_name, file_analyses)
        
        # Generate knowledge base using Gemini
        knowledge_base = await self._generate_knowledge_base(context)
        
        logger.info(f"Knowledge base built successfully")
        return knowledge_base
    
    def _prepare_context(
        self,
        project_name: str,
        file_analyses: List[Dict[str, Any]],
    ) -> str:
        """Prepare context string from all file analyses."""
        context_parts = [
            f"项目名称：{project_name}",
            f"共分析了 {len(file_analyses)} 个文件",
            "",
            "=== 文件分析结果汇总 ===",
            ""
        ]
        
        for i, analysis in enumerate(file_analyses, 1):
            filename = analysis.get('filename', f'文件{i}')
            file_type = analysis.get('file_type', 'unknown')
            result = analysis.get('analysis', {})
            
            context_parts.append(f"## 文件 {i}: {filename} ({file_type})")
            context_parts.append("")
            
            # Summary
            if 'summary' in result:
                context_parts.append(f"**概述**: {result['summary']}")
                context_parts.append("")
            
            # Entities
            if 'entities' in result and result['entities']:
                context_parts.append(f"**关键实体**: {', '.join(result['entities'][:10])}")
                context_parts.append("")
            
            # UI Info
            if 'ui_info' in result and result['ui_info']:
                context_parts.append(f"**UI信息**: {json.dumps(result['ui_info'], ensure_ascii=False)}")
                context_parts.append("")
            
            # Tech Info
            if 'tech_info' in result and result['tech_info']:
                context_parts.append(f"**技术约定**: {json.dumps(result['tech_info'], ensure_ascii=False)}")
                context_parts.append("")
            
            # References
            if 'references' in result and result['references']:
                context_parts.append(f"**重要引用**: {'; '.join(result['references'][:5])}")
                context_parts.append("")
            
            context_parts.append("---")
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    async def _generate_knowledge_base(self, context: str) -> Dict[str, Any]:
        """Generate structured knowledge base using Gemini."""
        prompt = f"""
请你作为一个资深的产品分析专家，深入分析以下项目文档，提取尽可能多的有价值信息，构建一个全面、详尽的项目知识库。

{context[:15000]}

请以JSON格式返回知识库，包含以下部分（请尽可能详细、全面地填充每个部分）：

## 1. project_overview (项目概览)
{{
  "product_name": "产品名称",
  "product_type": "产品类型（Web应用/移动应用/小程序等）",
  "target_users": "目标用户群体（详细描述）",
  "core_value": "核心价值主张",
  "business_model": "商业模式",
  "competitive_advantage": ["竞争优势1", "竞争优势2"],
  "description": "产品详细描述（200-500字）"
}}

## 2. functional_architecture (功能架构) - 重要！请详细列出
{{
  "modules": [
    {{
      "name": "模块名称",
      "description": "模块描述",
      "priority": "high/medium/low",
      "features": [
        {{
          "name": "功能名称",
          "description": "功能详细描述",
          "user_story": "作为...我想要...以便...",
          "acceptance_criteria": ["验收标准1", "验收标准2"],
          "priority": "P0/P1/P2"
        }}
      ]
    }}
  ]
}}

## 3. user_experience (用户体验)
{{
  "personas": [
    {{
      "name": "用户画像名称",
      "description": "用户描述",
      "goals": ["目标1", "目标2"],
      "pain_points": ["痛点1", "痛点2"]
    }}
  ],
  "user_journeys": [
    {{
      "scenario": "场景名称",
      "steps": ["步骤1", "步骤2"],
      "touchpoints": ["触点1", "触点2"]
    }}
  ],
  "key_interactions": ["关键交互模式1", "关键交互模式2"]
}}

## 4. ui_ux_design (UI/UX设计系统) - 详细提取设计元素
{{
  "design_system": {{
    "colors": {{
      "primary": "#颜色值",
      "secondary": "#颜色值",
      "success": "#颜色值",
      "warning": "#颜色值",
      "error": "#颜色值",
      "neutral": ["#颜色1", "#颜色2"]
    }},
    "typography": {{
      "font_family": "字体族",
      "font_sizes": {{"h1": "大小", "body": "大小"}},
      "line_heights": {{"tight": "值", "normal": "值"}}
    }},
    "spacing": {{
      "unit": "基本单位（如4px）",
      "scale": ["4px", "8px", "16px", "24px", "32px"]
    }},
    "border_radius": {{"small": "值", "medium": "值", "large": "值"}},
    "shadows": {{"small": "值", "medium": "值", "large": "值"}},
    "breakpoints": {{"mobile": "值", "tablet": "值", "desktop": "值"}}
  }},
  "components": [
    {{
      "name": "组件名称",
      "variants": ["变体1", "变体2"],
      "states": ["正常", "悬停", "激活", "禁用"],
      "usage": "使用场景"
    }}
  ],
  "layout_patterns": ["布局模式1", "布局模式2"],
  "responsive_strategy": "响应式策略说明",
  "animation_principles": ["动效原则1", "动效原则2"],
  "accessibility": ["无障碍特性1", "无障碍特性2"]
}}

## 5. technical_architecture (技术架构)
{{
  "tech_stack": {{
    "frontend": ["技术1", "技术2"],
    "backend": ["技术1", "技术2"],
    "database": ["数据库1"],
    "infrastructure": ["基础设施1"]
  }},
  "architecture_pattern": "架构模式（MVC/MVVM/微服务等）",
  "api_design": {{
    "style": "RESTful/GraphQL/RPC",
    "auth_method": "认证方式",
    "versioning": "版本控制策略",
    "endpoints": [
      {{
        "path": "/api/path",
        "method": "GET/POST",
        "description": "接口说明",
        "params": ["参数1", "参数2"]
      }}
    ]
  }},
  "third_party_integrations": [
    {{
      "service": "第三方服务名称",
      "purpose": "集成目的",
      "api_key_required": true
    }}
  ],
  "security_measures": ["安全措施1", "安全措施2"]
}}

## 6. data_model (数据模型) - 尽可能详细
{{
  "entities": [
    {{
      "name": "实体名称",
      "description": "实体描述",
      "fields": [
        {{
          "name": "字段名",
          "type": "数据类型",
          "required": true/false,
          "description": "字段说明",
          "validation": "验证规则",
          "example": "示例值"
        }}
      ],
      "relationships": [
        {{
          "target": "关联实体",
          "type": "one-to-many/many-to-many",
          "description": "关系说明"
        }}
      ]
    }}
  ]
}}

## 7. business_rules (业务规则)
{{
  "rules": [
    {{
      "name": "规则名称",
      "description": "规则描述",
      "conditions": ["条件1", "条件2"],
      "actions": ["动作1", "动作2"]
    }}
  ],
  "validation_rules": [
    {{
      "field": "字段名",
      "rules": ["规则1", "规则2"],
      "error_message": "错误提示"
    }}
  ],
  "permissions": [
    {{
      "role": "角色名称",
      "permissions": ["权限1", "权限2"]
    }}
  ],
  "workflows": [
    {{
      "name": "工作流名称",
      "steps": ["步骤1", "步骤2"],
      "actors": ["参与者1", "参与者2"]
    }}
  ]
}}

## 8. non_functional_requirements (非功能需求)
{{
  "performance": {{
    "response_time": "响应时间要求",
    "throughput": "吞吐量要求",
    "concurrent_users": "并发用户数"
  }},
  "reliability": {{
    "availability": "可用性目标（如99.9%）",
    "error_rate": "错误率要求"
  }},
  "scalability": {{
    "horizontal": "水平扩展策略",
    "vertical": "垂直扩展策略"
  }},
  "compatibility": {{
    "browsers": ["浏览器1", "浏览器2"],
    "devices": ["设备类型1", "设备类型2"],
    "os": ["操作系统1", "操作系统2"]
  }}
}}

## 9. pending_questions (待确认问题)
[
  {{
    "category": "功能/技术/UI/业务",
    "question": "具体问题",
    "context": "问题背景",
    "suggested_answer": "建议答案",
    "priority": "high/medium/low"
  }}
]

## 10. system_overview (保留旧格式兼容)
{{
  "product_type": "产品类型",
  "core_modules": ["模块1", "模块2"],
  "description": "系统描述"
}}

## 11. ui_standards (保留旧格式兼容)
{{
  "primary_colors": ["#颜色1", "#颜色2"],
  "component_library": "组件库名称",
  "layout_features": ["特征1", "特征2"]
}}

## 12. tech_conventions (保留旧格式兼容)
{{
  "naming_style": "camelCase/snake_case",
  "api_style": "RESTful/GraphQL",
  "known_fields": [
    {{"name": "字段名", "type": "类型", "usage": "用途"}}
  ]
}}

**重要提示**：
1. 请尽可能详细地填充每个字段，不要留空
2. 从文档中挖掘所有可能的信息
3. 对于不确定的内容，基于行业最佳实践进行合理推断
4. 功能架构（functional_architecture）是最重要的部分，请特别详细
5. 数据模型（data_model）请尽可能完整地列出所有实体和字段
6. 返回有效的JSON格式，不要包含markdown代码块标记

请开始分析并返回JSON：
"""
        
        try:
            response = await gemini_service.generate_text(
                prompt=prompt,
                system_instruction="你是一个专业的产品需求分析助手，擅长整合多个文档的信息，生成结构化的项目知识库。请始终返回有效的JSON格式。",
                temperature=0.3,
            )
            
            # Parse JSON response
            try:
                # Remove markdown code blocks if present
                clean_response = response.strip()
                if clean_response.startswith("```json"):
                    clean_response = clean_response[7:]
                if clean_response.startswith("```"):
                    clean_response = clean_response[3:]
                if clean_response.endswith("```"):
                    clean_response = clean_response[:-3]
                
                knowledge_base = json.loads(clean_response.strip())
                
                # Validate structure
                if not isinstance(knowledge_base, dict):
                    raise ValueError("Knowledge base must be a dictionary")
                
                # Ensure all required keys exist
                default_structure = {
                    "system_overview": {
                        "product_type": None,
                        "core_modules": [],
                        "description": None
                    },
                    "ui_standards": {
                        "primary_colors": [],
                        "component_library": None,
                        "layout_features": []
                    },
                    "tech_conventions": {
                        "naming_style": None,
                        "api_style": None,
                        "known_fields": []
                    },
                    "pending_questions": [],
                    "raw_insights": []
                }
                
                # Merge with defaults
                for key, default_value in default_structure.items():
                    if key not in knowledge_base:
                        knowledge_base[key] = default_value
                    elif isinstance(default_value, dict):
                        for subkey, subvalue in default_value.items():
                            if subkey not in knowledge_base[key]:
                                knowledge_base[key][subkey] = subvalue
                
                return knowledge_base
            
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Response: {response[:500]}")
                
                # Return a basic structure with the raw response
                return {
                    "system_overview": {
                        "product_type": "未知",
                        "core_modules": [],
                        "description": response[:200]
                    },
                    "ui_standards": {
                        "primary_colors": [],
                        "component_library": None,
                        "layout_features": []
                    },
                    "tech_conventions": {
                        "naming_style": None,
                        "api_style": None,
                        "known_fields": []
                    },
                    "pending_questions": [
                        {
                            "question": "AI生成的知识库格式有误，需要手动整理",
                            "context": "Gemini返回的不是有效的JSON格式",
                            "suggested_answer": None
                        }
                    ],
                    "raw_insights": [response[:500]]
                }
        
        except Exception as e:
            logger.error(f"Error generating knowledge base: {str(e)}")
            raise


# Global instance
knowledge_builder = KnowledgeBuilder()

