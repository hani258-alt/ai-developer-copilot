"""模块3：报错诊断助手 - 分析Python/Java/前端报错并提供解决方案"""

import os
import re
from typing import Dict, Any
from langchain_deepseek import ChatDeepSeek
from langchain_core.prompts import ChatPromptTemplate


class ErrorDiagnosis:
    """报错诊断助手"""
    
    def __init__(self):
        self.llm = ChatDeepSeek(
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-v3"),
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            api_base=os.getenv("DEEPSEEK_API_BASE"),
            temperature=0.3
        )
        
    def _detect_error_type(self, error_text: str) -> str:
        """自动检测报错类型"""
        python_patterns = [
            r"Traceback \(most recent call last\)",
            r"ImportError",
            r"NameError",
            r"TypeError",
            r"ValueError",
            r"AttributeError"
        ]
        
        java_patterns = [
            r"Exception in thread",
            r"java\.\w+Exception",
            r"ClassNotFoundException",
            r"NullPointerException"
        ]
        
        frontend_patterns = [
            r"Uncaught TypeError",
            r"ReferenceError",
            r"ReactDOMError",
            r"Cannot read property",
            r"Unexpected token"
        ]
        
        for pattern in python_patterns:
            if re.search(pattern, error_text):
                return "python"
                
        for pattern in java_patterns:
            if re.search(pattern, error_text):
                return "java"
                
        for pattern in frontend_patterns:
            if re.search(pattern, error_text):
                return "frontend"
                
        return "unknown"
        
    def _get_system_prompt(self, error_type: str) -> str:
        """获取对应类型的系统提示词"""
        prompts = {
            "python": """你是一位资深Python开发专家。请分析以下Python报错信息，用中文给出：
1. 报错原因分析
2. 具体的解决方案
3. 修改后的代码示例（如果适用）
请确保回答准确、实用。""",
            "java": """你是一位资深Java开发专家。请分析以下Java报错信息，用中文给出：
1. 报错原因分析
2. 具体的解决方案
3. 修改后的代码示例（如果适用）
请确保回答准确、实用。""",
            "frontend": """你是一位资深前端开发专家。请分析以下前端报错信息，用中文给出：
1. 报错原因分析
2. 具体的解决方案
3. 修改后的代码示例（如果适用）
请确保回答准确、实用。""",
            "unknown": """你是一位资深全栈开发专家。请分析以下报错信息，用中文给出：
1. 报错原因分析
2. 具体的解决方案
3. 修改后的代码示例（如果适用）
请确保回答准确、实用。"""
        }
        return prompts.get(error_type, prompts["unknown"])
        
    def diagnose_error(self, error_text: str, context_code: str = "") -> Dict[str, Any]:
        """诊断报错
        
        Args:
            error_text: 报错文本
            context_code: 相关上下文代码（可选）
            
        Returns:
            诊断结果
        """
        error_type = self._detect_error_type(error_text)
        
        user_prompt = f"""报错信息：
{error_text}
"""
        
        if context_code:
            user_prompt += f"""
相关代码：
{context_code}
"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt(error_type)),
            ("human", user_prompt)
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({})
        
        return {
            "error_type": error_type,
            "diagnosis": response.content,
            "raw_error": error_text
        }
        
    def generate_fixed_code(self, error_text: str, original_code: str) -> str:
        """生成修复后的代码"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一位资深代码修复专家。请根据报错信息，修复以下代码。
请只输出修复后的完整代码，不要添加其他解释。"""),
            ("human", """报错信息：
{error_text}

原始代码：
{original_code}
""")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({"error_text": error_text, "original_code": original_code})
        
        return response.content
        
    def quick_fix(self, error_text: str, original_code: str = "") -> Dict[str, Any]:
        """快速修复：诊断 + 代码修复"""
        diagnosis = self.diagnose_error(error_text, original_code)
        
        fixed_code = None
        if original_code:
            fixed_code = self.generate_fixed_code(error_text, original_code)
            
        return {
            **diagnosis,
            "fixed_code": fixed_code
        }
