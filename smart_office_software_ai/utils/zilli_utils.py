import os

from dotenv import load_dotenv
from pymilvus import MilvusClient

from model.embeddings import get_embeddings
# 加载环境变量
load_dotenv()

embeddings = get_embeddings()
d = embeddings.embed_query("你好")
CLUSTER_ENDPOINT = os.environ.get('CLUSTER_ENDPOINT')
TOKEN = os.environ.get('ZILLIZ_TOKEN')
client = MilvusClient(
    uri=CLUSTER_ENDPOINT,
    token=TOKEN
)

def insert(data):
    res = client.insert(
        collection_name="demo2",
        data=data
    )


def delete(ids):
    res = client.delete(
        collection_name="demo2",
        ids=ids
    )


def get(ids):
    res = client.get(
        collection_name="demo2",
        ids=ids
    )


def delete_by_file_id(file_id):
    """通过文件ID删除所有相关数据"""
    # 1. 先查询出该file_id对应的所有数据
    query_results = query_by_scalar("file_id", file_id)

    if not query_results:
        print(f"没有找到file_id为{file_id}的数据")
        return None

    # 2. 提取所有要删除的数据ID
    ids_to_delete = [item["primary_key"] for item in query_results]

    # 3. 执行删除操作
    return delete(ids_to_delete)


def query_by_scalar(field_name, value):
    expr = f"{field_name} == {value}"

    # 按位置传递核心参数（集合名、查询条件、返回字段）
    res = client.query(
        "demo2",  # 第一个参数：集合名（位置参数）
        expr,  # 第二个参数：查询条件（位置参数）
        ["*"]  # 第三个参数：返回字段（位置参数）
    )
    return res


if __name__ == '__main__':
    d = [
        {
            # 生成一个 384 维的向量（此处用随机数示例，实际应替换为你的真实向量）
            "vector_data": d,
            "chunk_id": 3,
            "file_id": 3
        }
    ]
    # get([459967549895317020])
    # insert(data)
    delete_by_file_id(9)
