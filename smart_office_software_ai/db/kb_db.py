import requests

from utils.mysql_utils import connect_mysql
from mysql.connector import Error
from model.embeddings import get_embeddings
from utils import zilli_utils
embeddings = get_embeddings()


def kb_list_db():
    conn = connect_mysql()
    cursor = conn.cursor(dictionary=True)
    try:
        sql = "SELECT * FROM kb"
        cursor.execute(sql)
        rows = cursor.fetchall()
        return rows
    except Error as err:
        conn.rollback()
        raise err
    finally:
        # 关闭游标和连接
        cursor.close()
        conn.close()


def dept_kb_list_db(dept_id):
    conn = connect_mysql()
    cursor = conn.cursor(dictionary=True)
    try:
        sql = """
        SELECT kb.id,kb.kb_name,kb.description,kb.created_at,updated_at,img
        FROM kb 
        INNER JOIN department_kb ON kb.id = department_kb.kb_id AND dept_id=%s
        """
        cursor.execute(sql, (dept_id,))
        rows = cursor.fetchall()
        return rows
    except Error as err:
        conn.rollback()
        raise err
    finally:
        # 关闭游标和连接
        cursor.close()
        conn.close()


def create_kb(kb_name, description):
    conn = connect_mysql()
    cursor = conn.cursor()
    try:
        # 使用 %s 作为占位符
        sql = "INSERT INTO kb (kb_name, description,is_public) VALUES (%s, %s,0)"
        cursor.execute(sql, (kb_name, description))
        # 提交事务
        conn.commit()
        # 返回插入的 ID（可选）
        return cursor.lastrowid
    except Exception as e:
        # 发生错误时回滚
        conn.rollback()
        raise e
    finally:
        # 关闭游标和连接
        cursor.close()
        conn.close()


def save_kb_dept_db(kb_id, dept_id):
    conn = connect_mysql()
    cursor = conn.cursor()
    try:
        sql = "INSERT INTO department_kb (kb_id, dept_id) VALUES (%s, %s)"
        cursor.execute(sql, (kb_id, dept_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def update_kb_db(kb_name, description, kb_id, img):  # 建议参数名用 kb_id 更明确
    conn = connect_mysql()
    cursor = conn.cursor()
    try:
        # 修正 UPDATE 语句的语法，使用逗号分隔多个字段
        sql = "UPDATE kb SET description = %s, kb_name = %s, img = %s WHERE id = %s"
        if img is None or img == "":
            img = "C:\\Users\\huang\\Pictures\\Saved Pictures\\11.png"
        cursor.execute(sql, (description, kb_name, img, kb_id))
        # 提交事务
        conn.commit()
        # 返回受影响的行数（可选）
        return cursor.rowcount
    except Exception as e:
        # 发生错误时回滚
        conn.rollback()
        raise e
    finally:
        # 关闭游标和连接
        cursor.close()
        conn.close()


def delete_kb_db(kb_id):
    conn = connect_mysql()
    cursor = conn.cursor()
    try:
        sql = "DELETE FROM kb WHERE id = %s"
        cursor.execute(sql, (kb_id,))
        conn.commit()
        return cursor.rowcount
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def get_public_kb_db():
    conn = connect_mysql()
    cursor = conn.cursor(dictionary=True)
    sql = "SELECT * FROM kb WHERE is_public = 1"
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def get_kb_db(kb_id):
    conn = connect_mysql()
    cursor = conn.cursor(dictionary=True)
    sql = "select * from kb where id = %s"
    try:
        cursor.execute(sql, (kb_id,))
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def get_kb_by_name_db(name):
    conn = connect_mysql()
    cursor = conn.cursor(dictionary=True)
    sql = "select * from kb where kb_name = %s"
    try:
        cursor.execute(sql, (name,))
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def save_doc_to_vector_db(split_docs, document_id):
    """
    将分割后的文档保存到知识库，包括插入文本块和向量索引。

    :param split_docs: 文档分割后的列表，每个元素应包含 page_content 属性（文档片段内容）
    :param document_id: 文档的id
    :return: 保存成功返回 (True, kb_id)，失败返回 (False, 错误描述)
    """
    conn = connect_mysql()
    cursor = conn.cursor()
    try:

        # 2. 插入文本块和向量索引
        for i, doc in enumerate(split_docs):
            # 插入文本块
            chunk_insert_query = """
                   INSERT INTO text_chunks (file_id, chunk_text, chunk_number)
                   VALUES (%s, %s, %s)
                   """
            chunk_params = (document_id, doc.page_content, i)
            cursor.execute(chunk_insert_query, chunk_params)
            # 获取最后插入的chunk_id
            chunk_id = cursor.lastrowid

            # 生成向量
            vector = embeddings.embed_query(doc.page_content)

            # 插入向量
            data = [
                {
                    "vector_data": vector,
                    "chunk_id": chunk_id,
                    "file_id": document_id
                }
            ]
            zilli_utils.insert(data)

        # 提交事务
        conn.commit()
        return True, document_id

    except Error as e:
        # 回滚事务
        conn.rollback()
        print(f"保存文档失败: {e}")
        return False, str(e)

    finally:
        # 关闭数据库连接
        if conn.is_connected():
            cursor.close()
            conn.close()


def get_text_chunks(document_id):
    conn = connect_mysql()
    cursor = conn.cursor()
    sql = "SELECT chunk_text, chunk_number FROM text_chunks where file_id = %s"
    try:
        cursor.execute(sql, (document_id,))
        chunks = cursor.fetchall()
        return chunks
    except Error as e:
        conn.rollback()
        return False, str(e)
    finally:
        cursor.close()
        conn.close()


def delete_text_chunks(document_id):
    conn = connect_mysql()
    cursor = conn.cursor()
    sql = "DELETE FROM text_chunks where file_id = %s"
    try:
        cursor.execute(sql, (document_id,))
        zilli_utils.delete_by_file_id(document_id)
        conn.commit()
        return True
    except Error as e:
        conn.rollback()
        return False, str(e)
    finally:
        cursor.close()
        conn.close()