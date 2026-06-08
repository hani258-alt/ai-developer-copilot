from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_and_split_documents(directory_path: str):
    """加载指定目录下所有文档文件并分割。

    支持的文件格式: PDF (.pdf), Markdown (.md), 文本文件 (.txt)

    Args:
        directory_path: 包含文档文件的目录路径

    Returns:
        分割后的 Document 对象列表
    """
    doc_dir = Path(directory_path)
    if not doc_dir.exists():
        raise FileNotFoundError(f"目录不存在: {directory_path}")

    # 支持的文件类型
    pdf_files = list(doc_dir.glob("*.pdf"))
    md_files = list(doc_dir.glob("*.md"))
    txt_files = list(doc_dir.glob("*.txt"))

    all_files = pdf_files + md_files + txt_files
    if not all_files:
        raise ValueError(f"目录中未找到支持的文档文件: {directory_path}\n支持的格式: .pdf, .md, .txt")

    print(f"找到 {len(pdf_files)} 个 PDF, {len(md_files)} 个 Markdown, {len(txt_files)} 个文本文件，开始加载...")

    # 加载所有文档
    all_docs = []
    for pdf_file in pdf_files:
        loader = PyPDFLoader(str(pdf_file))
        docs = loader.load()
        print(f"  加载PDF: {pdf_file.name} ({len(docs)} 页)")
        all_docs.extend(docs)

    for md_file in md_files:
        # 使用 TextLoader 读取 Markdown，避免安装 unstructured
        loader = TextLoader(str(md_file), encoding="utf-8")
        docs = loader.load()
        # 将文件类型标记为 markdown
        for doc in docs:
            doc.metadata["file_type"] = "markdown"
        print(f"  加载Markdown: {md_file.name}")
        all_docs.extend(docs)

    for txt_file in txt_files:
        loader = TextLoader(str(txt_file), encoding="utf-8")
        docs = loader.load()
        for doc in docs:
            doc.metadata["file_type"] = "text"
        print(f"  加载文本: {txt_file.name}")
        all_docs.extend(docs)

    print(f"共加载 {len(all_docs)} 个文档片段")

    # 分割文档
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
        separators=["\n\n", "\n", "。", "!", "！", ".", " ", ""],
    )
    chunks = splitter.split_documents(all_docs)

    print(f"分割为 {len(chunks)} 个文本块")
    return chunks


if __name__ == "__main__":
    # 示例用法
    test_dir = Path(__file__).parent / "docs"
    test_dir.mkdir(exist_ok=True)
    chunks = load_and_split_documents(str(test_dir))
    if chunks:
        print(f"\n第一个块预览:\n{chunks[0].page_content[:200]}...")
        print(f"\n来源: {chunks[0].metadata.get('source')}")
