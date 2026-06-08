import os
from pathlib import Path

from dotenv import load_dotenv
from chromadb import PersistentClient

load_dotenv()


def get_embeddings():
    """创建嵌入模型（自定义包装器，兼容 LangChain Embeddings 接口）。

    直接使用 OpenAI SDK 绕过 langchain_openai.OpenAIEmbeddings
    与百炼 API 的兼容问题。

    默认使用 text-embedding-v3（千问 Embedding）：
    - 推荐维度: 1024（可选 1024/768/512/256/128/64）
    - 最大输入: 8,192 tokens
    - 支持 50+ 语种 + 中英双语优化

    如需升级到 v4，修改 .env 中的 DEEPSEEK_EMBEDDING_MODEL=text-embedding-v4
    """
    # 延迟导入避免循环依赖
    from embeddings import DashScopeEmbeddings

    return DashScopeEmbeddings(
        model=os.environ.get("DEEPSEEK_EMBEDDING_MODEL", "text-embedding-v3"),
        api_key=os.environ["DEEPSEEK_API_KEY"],
        base_url=os.environ["DEEPSEEK_API_BASE"],
    )


def create_vector_store(chunks, persist_dir: str):
    """将文档块向量化并持久化到 Chroma。

    Args:
        chunks: Document 对象列表（来自 document_loader）
        persist_dir: Chroma 数据持久化目录

    Returns:
        配置好的嵌入模型实例（供后续检索复用）
    """
    store_dir = Path(persist_dir)
    if store_dir.exists():
        print(f"警告: 向量库目录已存在，将复用已有数据: {persist_dir}")
        print("如需重建，请先删除该目录")
        return get_embeddings()

    print(f"开始向量化，共 {len(chunks)} 个文本块...")

    embeddings = get_embeddings()

    # 使用 Chroma 持久化客户端
    client = PersistentClient(path=str(store_dir))

    # 检查集合是否已存在
    if client.get_or_create_collection("documents").count() > 0:
        print("向量库已包含数据，跳过构建")
        return embeddings

    collection = client.get_or_create_collection("documents")

    # 批量向量化并存储（Chroma 内部会自动调用 embedding function）
    # 但这里我们手动控制进度，逐批处理
    texts = [chunk.page_content for chunk in chunks]
    # 防御处理：Chroma 要求 metadatas 每个元素都是非空 dict
    safe_metadatas = [m if isinstance(m, dict) else {"source": "unknown"} for m in (chunk.metadata for chunk in chunks)]
    ids = [f"chunk_{i}" for i in range(len(chunks))]

    batch_size = 50
    for i in range(0, len(texts), batch_size):
        batch_end = min(i + batch_size, len(texts))
        batch_texts = texts[i:batch_end]
        batch_metadatas = safe_metadatas[i:batch_end]
        batch_ids = ids[i:batch_end]

        batch_embeddings = embeddings.embed_documents(batch_texts)
        collection.add(
            documents=batch_texts,
            metadatas=batch_metadatas,
            embeddings=batch_embeddings,
            ids=batch_ids,
        )
        print(f"  进度: {batch_end}/{len(texts)} ({batch_end / len(texts) * 100:.0f}%)")

    print(f"向量化完成！数据已保存到: {persist_dir}")
    return embeddings


if __name__ == "__main__":
    from document_loader import load_and_split_documents

    test_dir = Path(__file__).parent / "docs"
    chunks = load_and_split_documents(str(test_dir))
    persist_dir = Path(__file__).parent / "chroma_db"
    create_vector_store(chunks, str(persist_dir))
