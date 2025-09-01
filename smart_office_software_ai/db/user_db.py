from utils.mysql_utils import connect_mysql


def get_user_info(user_id):
    conn = connect_mysql()
    cursor = conn.cursor(dictionary=True)
    sql = "SELECT * FROM user WHERE id = %s"
    try:
        cursor.execute(sql,(user_id,))
        result = cursor.fetchall()
        return result
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        cursor.close()
        conn.close()