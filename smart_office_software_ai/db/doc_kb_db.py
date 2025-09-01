from utils.mysql_utils import connect_mysql


def delete_doc_kb_by_doc_id_db(doc_id):
    """
        在删除某个文档时也要将doc_kb表中的对应记录删掉
    """
    conn = connect_mysql()
    cursor = conn.cursor()
    sql = "DELETE FROM doc_kb WHERE file_id = %s"
    try:
        cursor.execute(sql, (doc_id,))
        conn.commit()
        return cursor.rowcount
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def add_doc_to_kb_db(kb_id, document_id):
    conn = connect_mysql()
    cursor = conn.cursor()
    sql = "INSERT INTO doc_kb (kb_id, file_id) VALUES (%s, %s)"
    try:
        cursor.execute(sql, (kb_id, document_id))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def delete_doc_from_kb_db(kb_id, document_id):
    conn = connect_mysql()
    cursor = conn.cursor()
    sql = "DELETE FROM doc_kb WHERE kb_id = %s and file_id = %s"
    try:
        cursor.execute(sql, (kb_id, document_id))
        conn.commit()
        return cursor.rowcount
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def delete_doc_kb_by_kb_id_db(kb_id):
    """
        在删除某个知识库时也要将doc_kb表中的对应记录删掉
    """
    conn = connect_mysql()
    cursor = conn.cursor()
    sql = "DELETE FROM doc_kb WHERE kb_id = %s"
    try:
        cursor.execute(sql, (kb_id,))
        conn.commit()
        return cursor.rowcount
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def get_doc_kb_by_kb_id_db(kb_id):
    """
        通过kb_id在doc_kb表中查找到所有对应的document_id
    """
    conn = connect_mysql()
    cursor = conn.cursor()
    sql = "SELECT file_id FROM doc_kb WHERE kb_id = %s"
    try:
        cursor.execute(sql, (kb_id,))
        result = cursor.fetchall()
        doc_id_list = [row[0] for row in result]
        return doc_id_list
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def delete_doc_kb_by_doc_id(doc_id):
    conn = connect_mysql()
    cursor = conn.cursor()
    sql = "DELETE FROM doc_kb WHERE file_id = %s"
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