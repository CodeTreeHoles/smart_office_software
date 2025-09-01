from datetime import datetime

from utils.mysql_utils import connect_mysql


def get_dept_by_user_id_db(user_id):
    sql = "SELECT * FROM department_user WHERE user_id=%s"
    conn = connect_mysql()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql, (user_id,))
        result = cursor.fetchall()
        return result
    except Exception as e:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()
