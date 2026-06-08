"""模块6：Agent系统 - 使用LangGraph实现智能代理"""

import os
from typing import Dict, Any, TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_deepseek import ChatDeepSeek
from modules.knowledge_base import KnowledgeBaseManager
from modules.code_analyzer import CodeAnalyzer
from modules.error_diagnosis import ErrorDiagnosis
from modules.note_generator import NoteGenerator


# 定义Agent状态
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], "list"]
    current_kb: str
    tool_outputs: Dict[str, Any]


class AgentSystem:
    """AI Developer Copilot Agent 系统"""
    
    def __init__(self):
        self.llm = ChatDeepSeek(
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-v3"),
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            api_base=os.getenv("DEEPSEEK_API_BASE"),
            temperature=0.3,
            streaming=True
        )
        
        self.kb_manager = KnowledgeBaseManager()
        self.code_analyzer = CodeAnalyzer()
        self.error_diagnosis = ErrorDiagnosis()
        self.note_generator = NoteGenerator()
        
        self.tools = self._register_tools()
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.graph = self._build_graph()
        
    def _register_tools(self):
        """注册Agent工具"""
        
        @tool
        def query_knowledge_base(query: str, kb_name: str = "default") -> str:
            """查询知识库，回答相关问题"""
            try:
                result = self.kb_manager.generate_answer(kb_name, query)
                return result
            except Exception as e:
                return f"查询知识库失败: {str(e)}"
                
        @tool
        def analyze_error(error_text: str) -> str:
            """分析报错信息，提供解决方案"""
            try:
                result = self.error_diagnosis.diagnose_error(error_text)
                return result["diagnosis"]
            except Exception as e:
                return f"报错分析失败: {str(e)}"
                
        @tool
        def analyze_code(code: str) -> str:
            """分析代码，提供改进建议"""
            prompt = f"""请分析以下代码，提供改进建议：
{code}
"""
            try:
                response = self.llm.invoke(prompt)
                return response.content
            except Exception as e:
                return f"代码分析失败: {str(e)}"
                
        @tool
        def generate_notes(topic: str) -> str:
            """生成学习笔记（摘要式）"""
            prompt = f"""请为以下主题生成一份学习笔记：
{topic}
"""
            try:
                response = self.llm.invoke(prompt)
                return response.content
            except Exception as e:
                return f"笔记生成失败: {str(e)}"
                
        return [query_knowledge_base, analyze_error, analyze_code, generate_notes]
        
    def _should_continue(self, state: AgentState):
        """判断是否需要继续执行"""
        messages = state["messages"]
        last_message = messages[-1]
        
        if last_message.tool_calls:
            return "tools"
        return END
        
    def _call_llm(self, state: AgentState):
        """调用LLM"""
        system_prompt = SystemMessage(content="""你是AI Developer Copilot，一位专业的开发助手。
你的职责是帮助开发者解决问题、学习知识、分析代码。
你可以使用以下工具：
- query_knowledge_base: 查询知识库
- analyze_error: 分析报错信息
- analyze_code: 分析代码
- generate_notes: 生成学习笔记

根据用户的问题，选择合适的工具来帮助用户。如果不需要工具，直接回答即可。
请使用中文回答。""")
        
        messages = [system_prompt] + list(state["messages"])
        response = self.llm_with_tools.invoke(messages)
        
        return {"messages": [response]}
        
    def _build_graph(self):
        """构建LangGraph"""
        workflow = StateGraph(AgentState)
        
        # 添加节点
        workflow.add_node("llm", self._call_llm)
        workflow.add_node("tools", ToolNode(self.tools))
        
        # 设置入口
        workflow.set_entry_point("llm")
        
        # 添加条件边
        workflow.add_conditional_edges(
            "llm",
            self._should_continue,
            {
                "tools": "tools",
                END: END
            }
        )
        
        workflow.add_edge("tools", "llm")
        
        return workflow.compile()
        
    def process_query(self, query: str, conversation_history: list = None) -> Dict[str, Any]:
        """处理用户查询
        
        Args:
            query: 用户查询
            conversation_history: 对话历史（可选）
            
        Returns:
            处理结果
        """
        messages = []
        
        if conversation_history:
            for msg in conversation_history:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                else:
                    messages.append(AIMessage(content=msg["content"]))
                    
        messages.append(HumanMessage(content=query))
        
        initial_state = {
            "messages": messages,
            "current_kb": "default",
            "tool_outputs": {}
        }
        
        # 执行图
        final_state = self.graph.invoke(initial_state)
        
        # 获取最终回答
        ai_messages = [
            msg for msg in final_state["messages"]
            if isinstance(msg, AIMessage) and not msg.tool_calls
        ]
        
        final_answer = ai_messages[-1].content if ai_messages else "抱歉，我无法处理这个问题。"
        
        return {
            "answer": final_answer,
            "messages": final_state["messages"],
            "tool_used": len(final_state["messages"]) > 2  # 简单判断是否使用了工具
        }
    
    def process_query_stream(self, query: str, conversation_history: list = None):
        """流式处理用户查询
        
        Args:
            query: 用户查询
            conversation_history: 对话历史（可选）
            
        Returns:
            流式生成器，逐块返回回答内容
        """
        from langchain_core.prompts import ChatPromptTemplate
        
        system_prompt = """你是AI Developer Copilot，一位专业的开发助手。
你的职责是帮助开发者解决问题、学习知识、分析代码。
请使用中文回答，语言简洁清晰。"""
        
        # 构建消息历史
        messages = [("system", system_prompt)]
        
        if conversation_history:
            for msg in conversation_history:
                role = "human" if msg["role"] == "user" else "ai"
                messages.append((role, msg["content"]))
        
        messages.append(("human", query))
        
        prompt = ChatPromptTemplate.from_messages(messages)
        chain = prompt | self.llm
        
        for chunk in chain.stream({}):
            yield chunk.content
