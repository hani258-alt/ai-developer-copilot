"""RAG 问答链（带对话记忆）：检索增强生成 + 多轮对话。

流程: 用户提问 -> Chroma 检索 -> 组装 Prompt（含上下文+历史） -> DeepSeek 生成答案
新增: 通过 InMemoryChatMessageHistory 维护每轮对话，模型能引用之前的问答。
"""

from __future__ import annotations

import os
from pathlib import Path
from collections import defaultdict

from dotenv import load_dotenv
from chromadb import PersistentClient
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_deepseek import ChatDeepSeek

load_dotenv()

# ─────────────────────────── 系统提示词 ───────────────────────────

SYSTEM_PROMPT = """你是一个知识库问答助手。请根据以下提供的上下文和对话历史来回答问题。

规则：
1. 优先根据上下文回答，不要编造不存在的信息。
2. 如果上下文中没有足够的信息，请直接说"根据提供的资料，我无法找到答案"。
3. 如果用户问的是关于之前对话的问题（如"刚才说到哪了"），请结合对话历史回答。
4. 回答要准确、简洁，使用中文。

上下文：
{context}
"""

# ─────────────────────────── 全局对话历史存储 ─────────────────────

# key: session_id, value: InMemoryChatMessageHistory
_session_histories: dict[str, InMemoryChatMessageHistory] = defaultdict(
    InMemoryChatMessageHistory
)


def get_history(session_id: str = "default") -> InMemoryChatMessageHistory:
    """获取指定会话的对话历史。"""
    return _session_histories[session_id]


def clear_history(session_id: str = "default") -> None:
    """清空指定会话的对话历史。"""
    if session_id in _session_histories:
        del _session_histories[session_id]


# ─────────────────────────── 核心函数 ───────────────────────────


def _format_docs(docs: list[dict]) -> str:
    """将检索到的文档块格式化为上下文字符串。"""
    if not docs:
        return "（未检索到相关文档）"
    return "\n\n---\n\n".join(
        f"[来源: {d.get('metadata', {}).get('source', 'unknown')}, 第 {d.get('metadata', {}).get('page', '?')} 页]\n{d['document']}"
        for d in docs
    )


def _format_history(history: InMemoryChatMessageHistory) -> str:
    """将对话历史格式化为可读字符串，注入系统提示词。"""
    if not history.messages:
        return "（无历史对话）"

    lines = []
    for msg in history.messages:
        role = "用户" if isinstance(msg, HumanMessage) else "助手"
        lines.append(f"{role}: {msg.content}")
    return "\n".join(lines)


def get_llm(model_type: str = "deepseek") -> Any:
    """根据模型类型创建相应的 LLM 实例"""
    if model_type == "deepseek":
        from langchain_deepseek import ChatDeepSeek
        return ChatDeepSeek(
            model=os.environ.get("DEEPSEEK_MODEL", "deepseek-v3"),
            api_key=os.environ["DEEPSEEK_API_KEY"],
            api_base=os.environ["DEEPSEEK_API_BASE"],
            temperature=0.3,
            max_tokens=2000,
        )
    elif model_type == "qwen":
        try:
            from langchain_community.chat_models import QwenChat
        except ImportError:
            raise ImportError("请安装 langchain-community: pip install langchain-community")
        return QwenChat(
            model_name=os.environ.get("QWEN_MODEL", "qwen-max"),
            qwen_api_key=os.environ["QWEN_API_KEY"],
            temperature=0.3,
            max_output_tokens=2000,
        )
    elif model_type == "openai":
        try:
            from langchain_openai import ChatOpenAI
        except ImportError:
            raise ImportError("请安装 langchain-openai: pip install langchain-openai")
        return ChatOpenAI(
            model=os.environ.get("OPENAI_MODEL", "gpt-4o"),
            api_key=os.environ["OPENAI_API_KEY"],
            base_url=os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1"),
            temperature=0.3,
            max_tokens=2000,
        )
    elif model_type == "anthropic":
        try:
            from langchain_anthropic import ChatAnthropic
        except ImportError:
            raise ImportError("请安装 langchain-anthropic: pip install langchain-anthropic")
        return ChatAnthropic(
            model=os.environ.get("ANTHROPIC_MODEL", "claude-3-haiku-20240307"),
            api_key=os.environ["ANTHROPIC_API_KEY"],
            temperature=0.3,
            max_tokens=2000
        )
    else:
        raise ValueError(f"不支持的模型类型: {model_type}")


def get_retriever(persist_dir: str, top_k: int = 4):
    """从持久化的 Chroma 创建检索器。

    返回一个函数: (query: str) -> list[dict]
    每个 dict 包含: document, metadata, distance
    """
    store_dir = Path(persist_dir)
    if not store_dir.exists():
        raise FileNotFoundError(
            f"向量库目录不存在: {persist_dir}\n"
            "请先运行 vector_store.py 构建向量库。"
        )

    client = PersistentClient(path=str(store_dir))
    collection = client.get_or_create_collection("documents")

    count = collection.count()
    if count == 0:
        raise ValueError(f"向量库为空: {persist_dir}")
    print(f"向量库已加载，共 {count} 条文档")

    from embeddings import DashScopeEmbeddings

    emb = DashScopeEmbeddings(
        model=os.environ.get("DEEPSEEK_EMBEDDING_MODEL", "text-embedding-v3"),
        api_key=os.environ["DEEPSEEK_API_KEY"],
        base_url=os.environ["DEEPSEEK_API_BASE"],
    )

    def retrieve(query: str) -> list[dict]:
        """检索与 query 最相关的 top_k 个文档。"""
        query_vec = emb.embed_query(query)
        results = collection.query(
            query_embeddings=[query_vec],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )
        docs = []
        for i in range(len(results["documents"][0])):
            docs.append({
                "document": results["documents"][0][i],
                "metadata": results["metadatas"][0][i] or {},
                "distance": results["distances"][0][i],
            })
        return docs

    return retrieve


def build_rag_chain(persist_dir: str, top_k: int = 4, session_id: str = "default", model_type: str = "deepseek"):
    """构建带对话记忆的 RAG 问答链（LCEL）。

    Args:
        persist_dir: Chroma 持久化目录
        top_k: 检索时返回的最相关文档数量
        session_id: 对话会话 ID（用于隔离不同用户的记忆）

    Returns:
        Runnable 链，输入 {"question": str}，输出 str 答案

    链结构:
        question -> retriever -> format_context+history -> prompt -> llm -> output
    """
    retriever = get_retriever(persist_dir, top_k=top_k)
    llm = get_llm(model_type)
    history = get_history(session_id)

    # Prompt：系统提示词 + 对话历史占位 + 用户问题
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
    ])

    # LCEL 链
    # LCEL 链
    chain = (
        {
            "context": lambda x: _format_docs(retriever(x["question"])),
            "chat_history": lambda x: history.messages,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain


# ─────────────────────────── 便捷函数 ───────────────────────────


def ask(
    question: str,
    persist_dir: str | None = None,
    top_k: int = 4,
    session_id: str = "default",
    model_type: str = "deepseek"  # 新增参数
) -> str:
    """带记忆的问答：检索文档 + 注入历史 → 生成答案 → 更新历史。

    Args:
        question: 用户问题
        persist_dir: 向量库目录（默认读取项目根目录下的 chroma_db）
        top_k: 检索文档数量
        session_id: 会话 ID，用于隔离不同用户的对话记忆

    Returns:
        模型生成的答案字符串
    """
    if persist_dir is None:
        persist_dir = str(Path(__file__).parent / "chroma_db")

    chain = build_rag_chain(persist_dir, top_k=top_k, session_id=session_id, model_type=model_type)
    answer = chain.invoke({"question": question})

    # 将本轮问答追加到记忆
    history = get_history(session_id)
    history.add_user_message(question)
    history.add_ai_message(answer)

    return answer


# ─────────────────────────── 主程序 ───────────────────────────

if __name__ == "__main__":
    persist_dir = str(Path(__file__).parent / "chroma_db")

    print("=" * 50)
    print("RAG 知识库问答系统（带对话记忆）")
    print("=" * 50)
    print(f"向量库路径: {persist_dir}")
    print("命令:")
    print("  clear   - 清空对话历史")
    print("  history - 查看对话历史")
    print("  quit / exit - 退出")
    print()

    while True:
        question = input("你: ").strip()
        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("再见！")
            break

        if question.lower() == "clear":
            clear_history()
            print("对话历史已清空。\n")
            continue

        if question.lower() == "history":
            history = get_history()
            if not history.messages:
                print("暂无对话历史。\n")
            else:
                print("\n--- 对话历史 ---")
                for msg in history.messages:
                    role = "你" if isinstance(msg, HumanMessage) else "AI"
                    # 截断过长内容
                    content = msg.content[:100] + ("..." if len(msg.content) > 100 else "")
                    print(f"  {role}: {content}")
                print("--- 结束 ---\n")
            continue

        try:
            answer = ask(question, persist_dir=persist_dir)
            print(f"\nAI: {answer}\n")
        except FileNotFoundError as e:
            print(f"\n错误: {e}\n")
            break
        except Exception as e:
            print(f"\n发生错误: {e}\n")
