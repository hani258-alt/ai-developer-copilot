"""模块1：智能知识库 - 支持多格式文档和多知识库管理"""

import os
import shutil
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_deepseek import ChatDeepSeek
from langchain_core.prompts import ChatPromptTemplate
from embeddings import get_embeddings

def _get_kb_dir_name(kb_name: str) -> str:
    """将知识库名称转换为安全的目录名（处理中文路径问题）"""
    # 使用MD5哈希确保目录名是ASCII字符，避免FAISS无法处理中文路径
    return hashlib.md5(kb_name.encode('utf-8')).hexdigest()


class KnowledgeBaseManager:
    """知识库管理器：支持多知识库、多格式文档"""
    
    def __init__(self, base_dir: str = "./knowledge_bases"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        self._kb_metadata_file = self.base_dir / "kb_metadata.json"
        self._load_kb_metadata()
        
    def _load_kb_metadata(self):
        if self._kb_metadata_file.exists():
            with open(self._kb_metadata_file, "r", encoding="utf-8") as f:
                self.kb_metadata = json.load(f)
        else:
            self.kb_metadata = {}
            
    def _save_kb_metadata(self):
        with open(self._kb_metadata_file, "w", encoding="utf-8") as f:
            json.dump(self.kb_metadata, f, ensure_ascii=False, indent=2)
            
    def create_kb(self, kb_name: str, description: str = "") -> bool:
        """创建新的知识库"""
        kb_dir = self.base_dir / _get_kb_dir_name(kb_name)
        if kb_dir.exists():
            return False
        
        kb_dir.mkdir()
        self.kb_metadata[kb_name] = {
            "description": description,
            "created_at": str(os.path.getctime(kb_dir)),
            "document_count": 0,
            "chunk_count": 0
        }
        self._save_kb_metadata()
        return True
        
    def list_kbs(self) -> List[Dict[str, Any]]:
        """列出所有知识库"""
        return [
            {
                "name": name,
                **metadata
            }
            for name, metadata in self.kb_metadata.items()
        ]
        
    def delete_kb(self, kb_name: str) -> bool:
        """删除知识库"""
        if kb_name not in self.kb_metadata:
            return False
            
        kb_dir = self.base_dir / _get_kb_dir_name(kb_name)
        if kb_dir.exists():
            shutil.rmtree(kb_dir)
            
        del self.kb_metadata[kb_name]
        self._save_kb_metadata()
        return True
        
    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名，移除危险字符但保留中文"""
        import re
        # 移除路径分隔符和其他危险字符，但保留中文、字母、数字、下划线、点号和中划线
        sanitized = re.sub(r'[\\/:*?"<>|]', '', filename)
        # 移除连续的点号和空格
        sanitized = re.sub(r'\.{2,}', '.', sanitized)
        sanitized = re.sub(r'\s+', ' ', sanitized)
        # 限制长度
        if len(sanitized) > 200:
            name, ext = os.path.splitext(sanitized)
            sanitized = name[:190] + ext
        return sanitized.strip()
        
    def _load_document(self, file_path: Path) -> List:
        """根据文件类型加载文档"""
        ext = file_path.suffix.lower()
        
        if ext == ".pdf":
            loader = PyPDFLoader(str(file_path))
        elif ext == ".docx":
            loader = Docx2txtLoader(str(file_path))
        elif ext in [".md", ".txt"]:
            loader = TextLoader(str(file_path), encoding="utf-8")
        else:
            raise ValueError(f"不支持的文件格式: {ext}")
            
        return loader.load()
        
    def add_document(self, kb_name: str, file_path: str, chunk_size: int = 500, chunk_overlap: int = 50, original_name: str = None) -> bool:
        """添加文档到知识库"""
        if kb_name not in self.kb_metadata:
            return False
            
        file = Path(file_path)
        if not file.exists():
            return False
            
        kb_dir = self.base_dir / _get_kb_dir_name(kb_name)
        docs_dir = kb_dir / "documents"
        docs_dir.mkdir(parents=True, exist_ok=True)
        
        # 保留原始文件名，如果没有提供则使用临时文件名
        target_name = original_name if original_name else file.name
        # 清理文件名中的危险字符
        target_name = self._sanitize_filename(target_name)
        
        # 复制文件到知识库
        shutil.copy(file, docs_dir / target_name)
        
        # 加载并分割文档
        docs = self._load_document(file)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "。", "！", "！", ".", " ", ""]
        )
        chunks = text_splitter.split_documents(docs)
        
        # 创建或更新向量存储
        faiss_dir = kb_dir / "faiss_index"
        embeddings = get_embeddings()
        
        # 检查faiss索引文件是否完整存在
        index_file = faiss_dir / "index.faiss"
        if faiss_dir.exists() and index_file.exists():
            try:
                vectorstore = FAISS.load_local(str(faiss_dir), embeddings, allow_dangerous_deserialization=True)
                vectorstore.add_documents(chunks)
            except Exception:
                # 如果加载失败，重新创建索引
                vectorstore = FAISS.from_documents(chunks, embeddings)
        else:
            vectorstore = FAISS.from_documents(chunks, embeddings)
            
        faiss_dir.mkdir(parents=True, exist_ok=True)
        vectorstore.save_local(str(faiss_dir))
        
        # 更新元数据
        self.kb_metadata[kb_name]["document_count"] = len(list(docs_dir.glob("*")))
        self.kb_metadata[kb_name]["chunk_count"] = vectorstore.index.ntotal
        self._save_kb_metadata()
        
        return True
        
    def list_documents(self, kb_name: str) -> List[str]:
        """列出知识库中的文档"""
        if kb_name not in self.kb_metadata:
            return []
            
        docs_dir = self.base_dir / _get_kb_dir_name(kb_name) / "documents"
        if not docs_dir.exists():
            return []
            
        return [f.name for f in docs_dir.glob("*")]
        
    def delete_document(self, kb_name: str, file_name: str) -> bool:
        """从知识库删除文档（需要重建索引）"""
        if kb_name not in self.kb_metadata:
            return False
            
        docs_dir = self.base_dir / _get_kb_dir_name(kb_name) / "documents"
        file = docs_dir / file_name
        
        if not file.exists():
            return False
            
        file.unlink()
        
        # 提示需要重建索引
        return True
        
    def rebuild_index(self, kb_name: str, chunk_size: int = 500, chunk_overlap: int = 50) -> bool:
        """重建知识库索引"""
        if kb_name not in self.kb_metadata:
            return False
            
        kb_dir = self.base_dir / _get_kb_dir_name(kb_name)
        docs_dir = kb_dir / "documents"
        
        if not docs_dir.exists():
            return False
            
        # 加载所有文档
        all_docs = []
        for file in docs_dir.glob("*"):
            try:
                docs = self._load_document(file)
                all_docs.extend(docs)
            except Exception as e:
                print(f"加载文档 {file.name} 失败: {e}")
                
        # 分割文档
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "。", "！", "！", ".", " ", ""]
        )
        chunks = text_splitter.split_documents(all_docs)
        
        # 创建新的向量存储
        faiss_dir = kb_dir / "faiss_index"
        embeddings = get_embeddings()
        vectorstore = FAISS.from_documents(chunks, embeddings)
        faiss_dir.mkdir(parents=True, exist_ok=True)
        vectorstore.save_local(str(faiss_dir))
        
        # 更新元数据
        self.kb_metadata[kb_name]["chunk_count"] = vectorstore.index.ntotal
        self._save_kb_metadata()
        
        return True
        
    def query_kb(self, kb_name: str, query: str, top_k: int = 4) -> Dict[str, Any]:
        """查询知识库，返回相关文档和来源"""
        if kb_name not in self.kb_metadata:
            return {"error": "知识库不存在"}
            
        kb_dir = self.base_dir / _get_kb_dir_name(kb_name)
        faiss_dir = kb_dir / "faiss_index"
        
        if not faiss_dir.exists():
            return {"error": "知识库未建立索引"}
            
        embeddings = get_embeddings()
        vectorstore = FAISS.load_local(str(faiss_dir), embeddings, allow_dangerous_deserialization=True)
        
        docs = vectorstore.similarity_search_with_score(query, k=top_k)
        
        results = []
        for doc, score in docs:
            results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": float(score)
            })
            
        return {"query": query, "results": results}
        
    def generate_answer(self, kb_name: str, query: str) -> str:
        """基于知识库内容生成带引用来源的答案"""
        query_result = self.query_kb(kb_name, query)
        
        if "error" in query_result:
            return query_result["error"]
            
        # 构建上下文
        context = ""
        sources = []
        for i, result in enumerate(query_result["results"]):
            source = result["metadata"].get("source", "unknown")
            page = result["metadata"].get("page", "?")
            context += f"[来源{i+1}: {source}, 第{page}页]\n{result['content']}\n\n"
            sources.append(f"来源{i+1}: {source}, 第{page}页")
            
        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个知识库问答助手。请根据以下上下文回答用户问题。回答要准确，使用中文。如果上下文中没有足够信息，请直接说明。"),
            ("human", "上下文:\n{context}\n\n问题: {query}")
        ])
        
        llm = ChatDeepSeek(
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-v3"),
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            api_base=os.getenv("DEEPSEEK_API_BASE"),
            temperature=0.3
        )
        
        chain = prompt | llm
        response = chain.invoke({"context": context, "query": query})
        
        answer = response.content
        answer += "\n\n**参考来源:**\n"
        answer += "\n".join(f"- {src}" for src in sources)
        
        return answer

    def get_stats(self) -> Dict[str, Any]:
        """获取知识库统计信息"""
        total_kbs = len(self.kb_metadata)
        total_docs = sum(kb.get("document_count", 0) for kb in self.kb_metadata.values())
        total_chunks = sum(kb.get("chunk_count", 0) for kb in self.kb_metadata.values())
        return {
            "total_kbs": total_kbs,
            "total_docs": total_docs,
            "total_chunks": total_chunks,
            "kbs": self.list_kbs()
        }
