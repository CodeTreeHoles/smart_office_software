

import time

from db.session_db import *

def get_session_server(session_id, limit=100, offset=0, sort_order='ASC'):
    """
    获取指定会话的聊天记录（支持分页和排序）
    复用已有的 get_chat_history_by_session 方法

    Args:
        session_id (str): 会话ID
        limit (int): 每页记录数，默认100
        offset (int): 偏移量，默认0
        sort_order (str): 排序方式，'ASC' 或 'DESC'，默认ASC

    Returns:
        list: 聊天记录列表
    """
    # 复用已有方法获取基础聊天记录
    records = get_chat_history_by_session(session_id, limit, offset)

    # 如果需要降序排列，反转列表（假设原方法返回ASC排序）
    if sort_order.upper() == 'DESC':
        records = records[::-1]

    # 获取会话信息
    session_info = get_session_info(session_id)

    # 为每条记录添加会话元数据（如果需要）
    if session_info:
        for record in records:
            record['user_id'] = session_info.get('user_id')
            record['session_start_time'] = session_info.get('start_time')
            record['session_metadata'] = session_info.get('metadata')

    return records


def raname_session_server(name, session_id):
    return raname_session_db(name, session_id)


def get_session_info_server(session_id):
    return get_session_info(session_id)


def delete_session_server(session_id):
    try:
        res1 = delete_chat_history(session_id)
        res2 = delete_session(session_id)
        if res1 and res2:
            return "删除成功"
        return "删除成功"
    except Exception as e:
        return f"出现异常，删除失败，{e}"


def create_session_server(user_id, session_name, metadata):
    try:
        session_id = str(user_id) + "-" + str(int(time.time()))
        create_new_session(session_id, session_name, user_id, metadata)
        return session_id
    except Exception as e:
        raise ""


def add_chat_record_server(session_id, role, content):
    """
    添加单条聊天记录并返回操作结果

    Args:
        session_id (str): 会话ID
        role (str): 角色（user/assistant）
        content (str): 消息内容
        create_time (datetime, optional): 消息创建时间，默认为当前时间

    Returns:
        dict: 包含操作结果和记录ID的响应
    """
    # 验证会话是否存在
    session_info = get_session_info(session_id)
    if not session_info:
        return {"success": False, "message": "会话不存在", "record_id": None}
    try:
        insert_chat_history(session_id, role, content)
        return {"success": True, "message": "添加成功", "record_id": None}
    except Exception as e:
        raise e
        # return False


def get_user_session_list_server(user_id):
    user_list = get_session_by_user_list(user_id)
    return user_list


if __name__ == '__main__':
    print(get_user_session_list_server(1))
