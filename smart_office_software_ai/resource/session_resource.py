from flask import Flask, request, jsonify
from flask_restful import Api, Resource

from db.kb_db import delete_kb_db
from server.rag_server import create_kb_server, delete_kb_server, get_kb_by_name_server, delete_doc_by_kb_id_server

delete_doc_by_kb_id_server
from server.session_server import *
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SessionResource(Resource):
    def get(self):
        """
        提供session_id即可
            获取某个会话的指定信息
        """
        data = request.get_json()
        session_id = data.get('session_id')
        if not session_id:
            return jsonify({"error": "Missing session_id"}), 400

        session_info = get_session_info_server(session_id)
        if not session_info:
            return jsonify({"error": "Session not found"}), 404

        return jsonify(session_info)

    def post(self):
        """
            创建一个新的会话
            需要传递用户的id和给会话所取的名字
        """
        data = request.get_json()
        user_id = data.get('user_id')
        session_name = data.get('session_name')  # 修正参数名
        metadata = data.get('metadata', {})  # 获取metadata，默认为空字典
        if not user_id or not session_name:
            return jsonify({"error": "Missing user_id or session_name"}), 400
        try:
            # 创建会话并传递metadata
            session_id = create_session_server(user_id, session_name, metadata)
            create_kb_server(session_id, f"{session_id}会话中上传的文件所构成的知识库")
            kb = get_kb_by_name_server(session_id)
            if session_id != "":
                return {
                    "success": True,
                    "session_id": session_id,
                    "message": "Session created successfully"
                }, 201
            else:
                return {"error": "Failed to create session"}, 500
        except Exception as e:
            return {"error": str(e)}, 500

    def put(self):
        data = request.get_json()
        session_id = data.get('session_id')
        name = data.get('name')
        res = raname_session_server(name, session_id)
        if res:
            return {'message': 'success'}, 200
        else:
            logger.error("重命名失败")
            return {'error': '重命名失败'}, 500


class DeleteSessionResource(Resource):
    def delete(self, session_id):
        res = delete_session_server(session_id)
        kb = get_kb_by_name_server(session_id)
        kb_id = kb[0].get("id")
        delete_doc_by_kb_id_server(kb_id)
        delete_kb_server(kb_id)
        logger.info(res)
        return jsonify(res)


class SessionListResource(Resource):
    def get(self, user_id):
        session_list = get_user_session_list_server(user_id)
        return jsonify(session_list)


class ChatHistoryResource(Resource):
    def get(self, session_id):
        chat_history = get_session_server(session_id)
        return jsonify(chat_history)

    def post(self, session_id):
        data = request.get_json()
        res = add_chat_record_server(session_id, data.get('role'), data.get('content'))
        return jsonify(res)
