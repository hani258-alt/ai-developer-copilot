"""模块5：对话记忆系统 - 支持多轮对话、上下文理解"""

import os
import json
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage


@dataclass
class ConversationMessage:
    """对话消息"""
    role: str
    content: str
    timestamp: str
    message_id: str


@dataclass
class ConversationSession:
    """对话会话"""
    session_id: str
    title: str
    created_at: str
    updated_at: str
    messages: List[ConversationMessage]


class ConversationMemory(BaseChatMessageHistory):
    """对话记忆系统"""
    
    def __init__(self, base_dir: str = "./conversation_history"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        self._current_session_id: str = None
        self._sessions: Dict[str, ConversationSession] = {}
        self._load_sessions()
        
    def _load_sessions(self):
        """加载所有会话"""
        for session_file in self.base_dir.glob("*.json"):
            try:
                with open(session_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    session = ConversationSession(**data)
                    self._sessions[session.session_id] = session
            except Exception as e:
                print(f"加载会话 {session_file} 失败: {e}")
                
    def _save_session(self, session_id: str):
        """保存会话"""
        if session_id not in self._sessions:
            return
            
        session = self._sessions[session_id]
        session_file = self.base_dir / f"{session_id}.json"
        
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(asdict(session), f, ensure_ascii=False, indent=2)
            
    def create_session(self, title: str = "新对话") -> str:
        """创建新会话"""
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        session = ConversationSession(
            session_id=session_id,
            title=title,
            created_at=str(datetime.now()),
            updated_at=str(datetime.now()),
            messages=[]
        )
        
        self._sessions[session_id] = session
        self._current_session_id = session_id
        self._save_session(session_id)
        
        return session_id
        
    def list_sessions(self) -> List[Dict[str, Any]]:
        """列出所有会话"""
        return [
            {
                "session_id": s.session_id,
                "title": s.title,
                "created_at": s.created_at,
                "updated_at": s.updated_at,
                "message_count": len(s.messages)
            }
            for s in self._sessions.values()
        ]
        
    def select_session(self, session_id: str) -> bool:
        """选择会话"""
        if session_id not in self._sessions:
            return False
        self._current_session_id = session_id
        return True
        
    def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        if session_id not in self._sessions:
            return False
            
        session_file = self.base_dir / f"{session_id}.json"
        if session_file.exists():
            session_file.unlink()
            
        del self._sessions[session_id]
        
        if self._current_session_id == session_id:
            self._current_session_id = None
            
        return True
        
    def rename_session(self, session_id: str, new_title: str) -> bool:
        """重命名会话"""
        if session_id not in self._sessions:
            return False
            
        session = self._sessions[session_id]
        session.title = new_title
        session.updated_at = str(datetime.now())
        self._save_session(session_id)
        
        return True
        
    @property
    def messages(self) -> List[BaseMessage]:
        """获取所有消息（兼容LangChain接口）"""
        if not self._current_session_id:
            return []
            
        session = self._sessions[self._current_session_id]
        result = []
        for msg in session.messages:
            if msg.role == "user":
                result.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                result.append(AIMessage(content=msg.content))
        return result
        
    def add_message(self, message: BaseMessage) -> None:
        """添加消息（兼容LangChain接口）"""
        if not self._current_session_id:
            self.create_session()
            
        session = self._sessions[self._current_session_id]
        
        role = "user" if isinstance(message, HumanMessage) else "assistant"
        conv_msg = ConversationMessage(
            role=role,
            content=message.content,
            timestamp=str(datetime.now()),
            message_id=f"msg_{len(session.messages)}"
        )
        
        session.messages.append(conv_msg)
        session.updated_at = str(datetime.now())
        self._save_session(self._current_session_id)
        
    def add_user_message(self, message: str) -> None:
        """添加用户消息"""
        self.add_message(HumanMessage(content=message))
        
    def add_ai_message(self, message: str) -> None:
        """添加AI消息"""
        self.add_message(AIMessage(content=message))
        
    def clear(self) -> None:
        """清空当前会话消息"""
        if not self._current_session_id:
            return
            
        session = self._sessions[self._current_session_id]
        session.messages = []
        session.updated_at = str(datetime.now())
        self._save_session(self._current_session_id)
        
    def get_conversation_history(self, limit: int = None) -> List[Dict[str, Any]]:
        """获取对话历史"""
        if not self._current_session_id:
            return []
            
        session = self._sessions[self._current_session_id]
        messages = session.messages
        
        if limit:
            messages = messages[-limit:]
            
        return [
            {
                "role": m.role,
                "content": m.content,
                "timestamp": m.timestamp
            }
            for m in messages
        ]
        
    def get_context(self, window_size: int = 5) -> str:
        """获取对话上下文"""
        history = self.get_conversation_history(limit=window_size)
        
        context = []
        for msg in history:
            role = "用户" if msg["role"] == "user" else "助手"
            context.append(f"{role}: {msg['content']}")
            
        return "\n".join(context)
