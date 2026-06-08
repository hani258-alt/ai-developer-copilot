"""模块4：学习笔记生成 - 从PDF/Markdown教程生成学习资料"""

import os
from pathlib import Path
from typing import Dict, List, Any
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_deepseek import ChatDeepSeek
from langchain_core.prompts import ChatPromptTemplate


class NoteGenerator:
    """学习笔记生成器"""
    
    def __init__(self):
        self.llm = ChatDeepSeek(
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-v3"),
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            api_base=os.getenv("DEEPSEEK_API_BASE"),
            temperature=0.3,
            streaming=True
        )
        
    def _load_document(self, file_path: str) -> str:
        """加载文档内容"""
        path = Path(file_path)
        ext = path.suffix.lower()
        
        if ext == ".pdf":
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            return "\n\n".join([doc.page_content for doc in docs])
        elif ext in [".md", ".txt"]:
            loader = TextLoader(file_path, encoding="utf-8")
            docs = loader.load()
            return "\n\n".join([doc.page_content for doc in docs])
        else:
            raise ValueError(f"不支持的文件格式: {ext}")
            
    def generate_notes(self, file_path: str) -> Dict[str, Any]:
        """生成完整学习笔记包
        
        Args:
            file_path: 教程文件路径（PDF/Markdown）
            
        Returns:
            包含学习笔记、面试题、知识总结、学习路线的字典
        """
        content = self._load_document(file_path)
        
        # 截取前20000字符避免token超限
        content_truncated = content[:20000]
        
        # 生成各部分内容
        study_notes = self._generate_study_notes(content_truncated)
        interview_questions = self._generate_interview_questions(content_truncated)
        knowledge_summary = self._generate_knowledge_summary(content_truncated)
        learning_roadmap = self._generate_learning_roadmap(content_truncated)
        
        return {
            "study_notes": study_notes,
            "interview_questions": interview_questions,
            "knowledge_summary": knowledge_summary,
            "learning_roadmap": learning_roadmap,
            "source_file": file_path
        }
    
    def generate_notes_stream(self, file_path: str) -> Dict[str, Any]:
        """流式生成学习笔记包
        
        Args:
            file_path: 教程文件路径（PDF/Markdown）
            
        Returns:
            包含各部分流式生成器的字典
        """
        content = self._load_document(file_path)
        
        # 截取前20000字符避免token超限
        content_truncated = content[:20000]
        
        return {
            "study_notes": self._generate_study_notes_stream(content_truncated),
            "interview_questions": self._generate_interview_questions_stream(content_truncated),
            "knowledge_summary": self._generate_knowledge_summary_stream(content_truncated),
            "learning_roadmap": self._generate_learning_roadmap_stream(content_truncated),
            "source_file": file_path
        }
        
    def _generate_study_notes(self, content: str) -> str:
        """生成学习笔记"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一位优秀的学习笔记整理专家。请根据以下教程内容，生成一份结构清晰的学习笔记。
要求：
1. 使用Markdown格式
2. 包含主要章节标题
3. 提取核心概念和关键点
4. 语言简洁，易于理解
5. 使用中文"""),
            ("human", "教程内容:\n{content}")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({"content": content})
        
        return response.content
    
    def _generate_study_notes_stream(self, content: str):
        """流式生成学习笔记"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一位优秀的学习笔记整理专家。请根据以下教程内容，生成一份结构清晰的学习笔记。
要求：
1. 使用Markdown格式
2. 包含主要章节标题
3. 提取核心概念和关键点
4. 语言简洁，易于理解
5. 使用中文"""),
            ("human", "教程内容:\n{content}")
        ])
        
        chain = prompt | self.llm
        for chunk in chain.stream({"content": content}):
            yield chunk.content
        
    def _generate_interview_questions(self, content: str) -> str:
        """生成面试题"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一位资深的技术面试官。请根据以下教程内容，生成一份面试题集。
要求：
1. 包含选择题、简答题、编程题
2. 题目难度分布合理（基础、进阶、高级）
3. 每个题目提供参考答案
4. 使用Markdown格式
5. 使用中文"""),
            ("human", "教程内容:\n{content}")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({"content": content})
        
        return response.content
    
    def _generate_interview_questions_stream(self, content: str):
        """流式生成面试题"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一位资深的技术面试官。请根据以下教程内容，生成一份面试题集。
要求：
1. 包含选择题、简答题、编程题
2. 题目难度分布合理（基础、进阶、高级）
3. 每个题目提供参考答案
4. 使用Markdown格式
5. 使用中文"""),
            ("human", "教程内容:\n{content}")
        ])
        
        chain = prompt | self.llm
        for chunk in chain.stream({"content": content}):
            yield chunk.content
        
    def _generate_knowledge_summary(self, content: str) -> str:
        """生成知识总结"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一位优秀的知识总结专家。请根据以下教程内容，生成一份知识体系总结。
要求：
1. 使用思维导图或列表形式展示知识结构
2. 提取核心知识点
3. 说明各知识点之间的关联
4. 使用Markdown格式
5. 使用中文"""),
            ("human", "教程内容:\n{content}")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({"content": content})
        
        return response.content
    
    def _generate_knowledge_summary_stream(self, content: str):
        """流式生成知识总结"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一位优秀的知识总结专家。请根据以下教程内容，生成一份知识体系总结。
要求：
1. 使用思维导图或列表形式展示知识结构
2. 提取核心知识点
3. 说明各知识点之间的关联
4. 使用Markdown格式
5. 使用中文"""),
            ("human", "教程内容:\n{content}")
        ])
        
        chain = prompt | self.llm
        for chunk in chain.stream({"content": content}):
            yield chunk.content
        
    def _generate_learning_roadmap(self, content: str) -> str:
        """生成学习路线图"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一位优秀的学习规划专家。请根据以下教程内容，生成一份学习路线图。
要求：
1. 分阶段规划（入门、进阶、精通）
2. 每个阶段说明学习目标和重点
3. 提供学习建议和时间估计
4. 推荐相关的练习和实践项目
5. 使用Markdown格式
6. 使用中文"""),
            ("human", "教程内容:\n{content}")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({"content": content})
        
        return response.content
    
    def _generate_learning_roadmap_stream(self, content: str):
        """流式生成学习路线图"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一位优秀的学习规划专家。请根据以下教程内容，生成一份学习路线图。
要求：
1. 分阶段规划（入门、进阶、精通）
2. 每个阶段说明学习目标和重点
3. 提供学习建议和时间估计
4. 推荐相关的练习和实践项目
5. 使用Markdown格式
6. 使用中文"""),
            ("human", "教程内容:\n{content}")
        ])
        
        chain = prompt | self.llm
        for chunk in chain.stream({"content": content}):
            yield chunk.content
        
    def export_markdown(self, notes_data: Dict[str, Any], output_dir: str = "./generated_notes") -> Dict[str, str]:
        """导出为Markdown文件
        
        Args:
            notes_data: generate_notes() 返回的字典
            output_dir: 输出目录
            
        Returns:
            导出的文件路径字典
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        source_name = Path(notes_data["source_file"]).stem
        
        files = {
            "study_notes": output_path / f"{source_name}_学习笔记.md",
            "interview_questions": output_path / f"{source_name}_面试题.md",
            "knowledge_summary": output_path / f"{source_name}_知识总结.md",
            "learning_roadmap": output_path / f"{source_name}_学习路线.md"
        }
        
        with open(files["study_notes"], "w", encoding="utf-8") as f:
            f.write(notes_data["study_notes"])
            
        with open(files["interview_questions"], "w", encoding="utf-8") as f:
            f.write(notes_data["interview_questions"])
            
        with open(files["knowledge_summary"], "w", encoding="utf-8") as f:
            f.write(notes_data["knowledge_summary"])
            
        with open(files["learning_roadmap"], "w", encoding="utf-8") as f:
            f.write(notes_data["learning_roadmap"])
            
        return {
            key: str(path)
            for key, path in files.items()
        }
