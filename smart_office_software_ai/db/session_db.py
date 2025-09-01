from utils.mysql_utils import connect_mysql
from datetime import datetime
import uuid


def insert_chat_history(session_id, role, content):
    """插入单条聊天记录"""
    conn = connect_mysql()
    cursor = conn.cursor()
    sql = "INSERT INTO chat_history (session_id, role, content, create_time) VALUES (%s, %s, %s, NOW())"
    try:
        cursor.execute(sql, (session_id, role, content))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def batch_insert_chat_history(records):
    """批量插入聊天记录"""
    conn = connect_mysql()
    cursor = conn.cursor()
    sql = "INSERT INTO chat_history (session_id, role, content, create_time) VALUES (%s, %s, %s, %s)"
    try:
        # 准备数据列表
        data_list = [(
            record["session_id"],
            record["role"],
            record["content"],
            record.get("create_time", datetime.now())
        ) for record in records]
        cursor.executemany(sql, data_list)
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def get_chat_history_by_session(session_id, limit=100, offset=0):
    """获取某个会话的聊天记录"""
    conn = connect_mysql()
    cursor = conn.cursor(dictionary=True)
    sql = """
    SELECT id, session_id, role, content, create_time 
    FROM chat_history 
    WHERE session_id = %s 
    ORDER BY create_time ASC 
    LIMIT %s OFFSET %s
    """
    try:
        cursor.execute(sql, (session_id, limit, offset))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


def get_latest_session_messages(user_id, limit=10):
    """获取用户最新会话的消息"""
    conn = connect_mysql()
    cursor = conn.cursor(dictionary=True)
    sql = """
    SELECT h.* 
    FROM chat_history h
    JOIN (
        SELECT id 
        FROM session 
        WHERE user_id = %s 
        ORDER BY start_time DESC 
        LIMIT 1
    ) s ON h.session_id = s.session_id
    ORDER BY h.create_time DESC 
    LIMIT %s
    """
    try:
        cursor.execute(sql, (user_id, limit))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


def update_chat_content(record_id, new_content):
    """更新聊天记录内容"""
    conn = connect_mysql()
    cursor = conn.cursor()
    sql = "UPDATE chat_history SET content = %s WHERE id = %s"
    try:
        cursor.execute(sql, (new_content, record_id))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def delete_session(session_id):
    conn = connect_mysql()
    cursor = conn.cursor()
    sql = "DELETE FROM session WHERE id = %s"
    try:
        cursor.execute(sql, (session_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def delete_chat_history(session_id=None, record_id=None):
    """删除聊天记录（可按会话或记录ID删除）"""
    conn = connect_mysql()
    cursor = conn.cursor()
    sql = "DELETE FROM chat_history WHERE session_id = %s"

    try:
        cursor.execute(sql, (session_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def create_new_session(session_id, session_name, user_id, metadata=None):
    """创建新会话"""
    conn = connect_mysql()
    cursor = conn.cursor()
    sql = "INSERT INTO session (id,name, start_time, user_id, metadata) VALUES (%s,%s, NOW(), %s, %s)"
    try:
        cursor.execute(sql, (session_id, session_name, user_id, str(metadata) if metadata else None))
        conn.commit()
        return session_id
    except Exception as e:
        conn.rollback()
        return None
    finally:
        cursor.close()
        conn.close()


def get_session_info(session_id):
    """获取会话信息"""
    conn = connect_mysql()
    cursor = conn.cursor(dictionary=True)
    sql = "SELECT * FROM session WHERE id = %s"
    try:
        cursor.execute(sql, (session_id,))
        return cursor.fetchone()
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


def get_session_by_user_list(user_id):
    conn = connect_mysql()
    cursor = conn.cursor(dictionary=True)
    sql = "SELECT * FROM session WHERE user_id = %s"
    try:
        cursor.execute(sql, (user_id,))
        list = cursor.fetchall()
        return list
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


def raname_session_db(name, session_id):
    conn = connect_mysql()
    cursor = conn.cursor()
    sql = "update session set name = %s where id = %s"
    try:
        cursor.execute(sql, (name, session_id,))
        conn.commit()
        return True
    except Exception as e:
        return False
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    print(raname_session_db("demo", "1-1749047702"))