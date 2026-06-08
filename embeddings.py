from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from langchain_core.embeddings import Embeddings

load_dotenv()


class DashScopeEmbeddings(Embeddings):
    """通过阿里云百炼 OpenAI 兼容接口调用嵌入模型。

    绕过 langchain_openai.OpenAIEmbeddings 的 with_raw_response 问题。
    """

    def __init__(
        self,
        model: str = "text-embedding-v3",
        api_key: str | None = None,
        base_url: str | None = None,
    ):
        self.model = model
        self.client = OpenAI(
            api_key=api_key or os.environ["DEEPSEEK_API_KEY"],
            base_url=base_url or os.environ["DEEPSEEK_API_BASE"],
        )

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """批量生成文档向量。"""
        # text-embedding-v4 等百炼模型有批次限制（max 10 per request）
        all_embeddings = []
        batch_size = 10
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            resp = self.client.embeddings.create(model=self.model, input=batch)
            batch_vecs = [d.embedding for d in resp.data]
            all_embeddings.extend(batch_vecs)
        return all_embeddings

    def embed_query(self, text: str) -> list[float]:
        """生成单个查询文本的向量。"""
        resp = self.client.embeddings.create(model=self.model, input=[text])
        return resp.data[0].embedding


def get_embeddings():
    """创建嵌入模型实例。"""
    return DashScopeEmbeddings(
        model=os.environ.get("DEEPSEEK_EMBEDDING_MODEL", "text-embedding-v3"),
        api_key=os.environ["DEEPSEEK_API_KEY"],
        base_url=os.environ["DEEPSEEK_API_BASE"],
    )


if __name__ == "__main__":
    emb = get_embeddings()

    # Test query embedding
    qvec = emb.embed_query("你好世界")
    print(f"Query vector dimension: {len(qvec)}")

    # Test doc embeddings
    docs = ["这是第一条测试文档", "这是第二条测试文档"]
    dvecs = emb.embed_documents(docs)
    print(f"Doc vector dimension: {len(dvecs[0])}")
    print(f"Count: {len(dvecs)} documents")

    print("\nSuccess!")
