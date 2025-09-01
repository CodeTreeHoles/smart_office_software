from datetime import datetime

from utils import zilli_utils
from utils.mysql_utils import connect_mysql


def get_doc_db(document_id):
    conn = connect_mysql()
    cursor = conn.cursor(dictionary=True)
    sql = "SELECT * FROM file WHERE id = %s"
    try:
        cursor.execute(sql, (document_id,))
        result = cursor.fetchone()
        conn.commit()
        return result
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def get_rag(doc_id_list):
    if not doc_id_list:  # 简化空列表判断
        return None

    # 1. 从 MySQL 获取文本片段和文件信息（不含向量）
    conn = connect_mysql()
    cursor = conn.cursor(dictionary=True)
    placeholders = ', '.join(['%s'] * len(doc_id_list))
    sql = f"""
    SELECT 
        tc.id AS chunk_id,
        tc.chunk_text,
        tc.chunk_number,
        tc.file_id,
        f.file_name
    FROM 
        text_chunks tc
    LEFT JOIN
        file f ON tc.file_id = f.id
    WHERE 
        tc.file_id IN ({placeholders})
    """

    try:
        cursor.execute(sql, doc_id_list)
        mysql_result = cursor.fetchall()  # MySQL 查询结果（文本信息）
        if not mysql_result:
            return None

        # 2. 从 Milvus 中查询每个 file_id 对应的向量数据
        # 按 file_id 分组，减少 Milvus 查询次数
        milvus_vector_map = {}  # 存储 {chunk_id: vector_data}

        for file_id in doc_id_list:
            # 调用 Milvus 标量查询，根据 file_id 获取向量数据
            milvus_results = zilli_utils.query_by_scalar("file_id", file_id)
            # 将 Milvus 结果按 chunk_id 映射（假设向量数据中包含 chunk_id）
            for vec_item in milvus_results:
                chunk_id = vec_item.get("chunk_id")  # 向量数据中的 chunk_id
                if chunk_id:
                    milvus_vector_map[chunk_id] = vec_item.get("vector_data")

        # 3. 合并 MySQL 文本信息和 Milvus 向量数据
        final_result = []
        for item in mysql_result:
            chunk_id = item['chunk_id']
            # 补充向量数据（若存在）
            item['vector_data'] = milvus_vector_map.get(chunk_id)
            final_result.append(item)

        return final_result

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def save_doc_db(file_url, file_name, user_id, scope, file_type):
    conn = connect_mysql()
    cursor = conn.cursor()
    sql = "INSERT INTO file (file_path,file_name,user_id,scope,file_type,created_at,updated_at) VALUES (%s,%s,%s,%s,%s,%s,%s)"
    try:
        cursor.execute(sql, (file_url, file_name, user_id, scope, file_type, datetime.now(), datetime.now()))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def get_doc_by_path_db(file_url):
    conn = connect_mysql()
    cursor = conn.cursor(dictionary=True)
    sql = "SELECT * FROM file WHERE file_path = %s"
    try:
        cursor.execute(sql, (file_url,))
        result = cursor.fetchall()
        return result
    except Exception as e:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def delete_doc_db(doc_id):
    conn = connect_mysql()
    cursor = conn.cursor()
    sql = "DELETE FROM file WHERE id = %s"
    try:
        cursor.execute(sql, (doc_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()
