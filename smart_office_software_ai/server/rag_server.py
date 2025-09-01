from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import RunnableConfig

from db.dept_db import get_dept_by_user_id_db
from utils.docs_utils import load_docs
from db.kb_db import *
from db.doc_kb_db import *
from db.doc_db import *
from utils.oss_utils import delete_file_by_url
from utils.retriever_utils import get_retriever
from langchain_core.tools import create_retriever_tool
from langchain.text_splitter import RecursiveCharacterTextSplitter
from utils.file_utils import filename_to_file
from typing import List, Dict, Any, Optional

embeddings = get_embeddings()


def save_doc_to_vector_server(file, document_id):
    """
    :param file:
    :param document_id:
        将指定的文档转换为向量存储在数据库中
    """
    # data_file = wash_data_utils.clean_data_file(file)
    to_file = filename_to_file(file)
    all_docs = load_docs(to_file)
    # 文本分割
    # 依据文档字符的个数来决定文本分割的策略
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200
    )
    split_docs = text_splitter.split_documents(all_docs)
    # 调用封装函数保存知识库
    save_doc_to_vector_db(split_docs, document_id)


def add_doc_to_kb_server(kb_id, document_id):
    """
    :param kb_id:
    :param document_id:
        将一个文档与一个知识库建立起联系
    """
    add_doc_to_kb_db(kb_id, document_id)
    # 去text_chunks表中查询看看，此文档是否有向量化
    chunks = get_text_chunks(document_id)
    if len(chunks) == 0:
        file_path = get_doc_db(document_id)['file_path']
        save_doc_to_vector_server(file_path, document_id)
    else:
        delete_text_chunks(document_id)
        file_path = get_doc_db(document_id)['file_path']
        save_doc_to_vector_server(file_path, document_id)


def delete_doc_from_kb_server(kb_id, document_id):
    """
    :param kb_id:
    :param document_id:
        将一个文档从知识库中删除，本质上是断开了联系，但是文档本身还在数据库中
    """
    delete_doc_from_kb_db(kb_id, document_id)


def create_kb_server(kb_name, description):
    """
    :param kb_name:知识库的名称
    :param description:知识库的描述信息
    创建一个新的知识库
    """
    return create_kb(kb_name, description)


def save_kb_dept_server(kb_id, dept_id):
    """
    :param kb_id:知识库id
    :param dept_id:部门id
    Args:
        kb_id:
        dept_id:

    Returns:
    """
    save_kb_dept_db(kb_id, dept_id)


def get_kb_server(kb_id):
    """获取知识库信息"""
    return get_kb_db(kb_id)


def get_public_kb_server():
    return get_public_kb_db()


def get_kb_by_name_server(name):
    """通过知识库名称来获取知识库信息"""
    return get_kb_by_name_db(name)


def update_kb_server(kb_name, description, kb_id, img):
    """更新知识库的描述信息"""
    return update_kb_db(kb_name, description, kb_id, img)


def delete_kb_server(kb_id):
    """删除知识库"""
    kb = get_kb_db(kb_id)
    if kb[0].get('is_public') == 1:
        return False
    try:
        delete_doc_kb_by_kb_id_db(kb_id)
        delete_kb_db(kb_id)
        return True
    except Exception as e:
        raise e


def delete_doc_by_kb_id_server(kb_id):
    list = get_doc_kb_by_kb_id_db(kb_id)
    for doc_id in list:
        doc = get_doc_db(doc_id)
        file_path = doc.get("file_path")
        delete_doc_db(doc_id)
        delete_text_chunks(doc_id)
        delete_file_by_url(file_path)


def kb_list_server():
    """获取所有的知识库的列表"""
    return kb_list_db()


def dept_kb_list_server(user_id):
    """获取指定部门的知识库列表"""
    dept = get_dept_by_user_id_db(user_id)
    if len(dept) == 0:
        return None
    dept_id = dept[0].get("dept_id")
    return dept_kb_list_db(dept_id)


class EmptyRetriever(BaseRetriever):
    """空检索器实现，当知识库没有文档时使用"""

    kb_id: Optional[int] = None  # 改为可选字段并提供默认值

    def __init__(self, kb_id: Optional[int] = None, **kwargs: Any):
        super().__init__(**kwargs)
        self.kb_id = kb_id

    def _get_relevant_documents(
            self,
            query: str,
            *,
            run_manager: Optional[CallbackManagerForRetrieverRun] = None
    ) -> List[Document]:
        return []

    def invoke(self, query: str, config: Optional[RunnableConfig] = None, **kwargs):
        return self._get_relevant_documents(query, run_manager=kwargs.get("run_manager"))


def get_retriever_tool(kb_id):
    """从数据库获取指定知识库并创建检索器工具"""
    doc_id_list = get_doc_kb_by_kb_id_db(kb_id)
    # 检查文档列表是否为空
    if len(doc_id_list) == 0:
        empty_retriever = EmptyRetriever(kb_id)
        return create_retriever_tool(
            retriever=empty_retriever,
            name=f"kb_{kb_id}_search",
            description=f"搜索知识库 {kb_id} 中的信息（当前为空）"
        )
    results = get_rag(doc_id_list)
    retriever = get_retriever(results)
    # 提取不重复的文件名列表
    file_names = list({result['file_name'] for result in results if result['file_name']})
    # 创建描述信息，包含文件名
    description = f"搜索知识库 {kb_id} 中的信息。包含文件: {', '.join(file_names)}"
    retriever_tool = create_retriever_tool(
        retriever,
        name=f"kb_{kb_id}_search",
        description=description
    )
    return retriever_tool

if __name__ == '__main__':
    get_retriever_tool(2)
def get_doc_by_kb_id_server(kb_id):
    doc_id_list = get_doc_kb_by_kb_id_db(kb_id)
    results = []
    for doc_id in doc_id_list:
        file = get_doc_db(doc_id)
        results.append(file)
    return results
