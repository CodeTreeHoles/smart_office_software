from model.embeddings import get_embeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from utils.vector_utils import bytes_to_vector


def get_retriever(tc):
    embeddings = get_embeddings()
    documents = []
    vectors = []
    title_text = tc[0]["chunk_text"]
    title_prefix = title_text[:20] if len(title_text) >= 20 else title_text

    for item in tc:
        file_id = item["file_id"]
        file_name = item["file_name"]
        chunk_number = item["chunk_number"]
        chunk_text = item["chunk_text"]
        vector_data = item["vector_data"]

        global_id = f"{file_id}_{chunk_number}"
        metadata = {
            "global_id": global_id,
            "file_id": file_name,
            "chunk_number": chunk_number,
            "timestamp": item.get("timestamp"),
            "content_type": item.get("content_type", "text"),
            "auto_title": f"{title_prefix}_段落"
        }

        doc = Document(
            page_content=chunk_text,
            metadata=metadata
        )

        if vector_data:
            if isinstance(vector_data, bytes):
                vector = bytes_to_vector(vector_data)
            else:
                vector = vector_data
        else:
            vector = embeddings.embed_query(chunk_text)

        documents.append(doc)
        vectors.append(vector)

    # 关键修改：直接使用预计算的向量创建FAISS索引
    vectorstore = FAISS.from_embeddings(
        text_embeddings=list(zip([d.page_content for d in documents], vectors)),
        embedding=embeddings,
        metadatas=[d.metadata for d in documents]
    )

    retriever = vectorstore.as_retriever()
    return retriever


# 正确示例：提供 func 参数
def search_knowledge_base(query: str) -> str:
    """在知识库中搜索与查询相关的信息"""
    # 实际的搜索实现
    return f"关于'{query}'的搜索结果..."
