from flask import request
from flask_restful import Resource
import redis
import json
from datetime import timedelta, datetime
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import logging
from model import model_llm_qwen
from prompts import hwchase17
from server.agent_server import public_tools
from server.doc_server import save_doc_server, delete_doc_server, get_doc_server
from server.rag_server import get_retriever_tool, get_kb_by_name_server, add_doc_to_kb_server, delete_doc_from_kb_server
from server.session_server import get_session_server, add_chat_record_server
from utils.agent_utils import DynamicAgentWrapper
from utils.oss_utils import delete_file_by_url

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
AGENT_CACHE_KEY_TEMPLATE = "agent:kb:%s"  # 缓存键模板，%s 为 kb_id
AGENT_CACHE_TTL = timedelta(hours=1)  # 缓存有效期：1小时

# ========== 初始化 Redis 缓存客户端 ==========
redis_client = redis.Redis(host='localhost', port=6379, db=0)  # 使用独立 DB 1 存储 Agent 缓存


class SingletonAgentManager:
    _instances = {}  # 存储已创建的 Agent

    @classmethod
    def get_agent(cls, kb_ids, session_id, user_info, temp_file_id_list=None):
        # 处理 session_id 为空的情况
        if not session_id:
            logger.warning("session_id 为空，无法获取或创建 Agent")
            return None

        if session_id not in cls._instances:
            try:
                kb_t = get_kb_by_name_server(session_id)
                kb_id_t = kb_t[0].get("id")
                tools = public_tools(kb_id_t)

                # 将用户id关联到agent中
                # user_info_tool = create_user_info_tool(user_info)
                # tools.append(user_info_tool)
                # 知识库检索工具
                if kb_ids is not None:
                    for kb_id in kb_ids:
                        kb_tool = get_retriever_tool(kb_id)
                        tools.append(kb_tool)

                # 创建动态代理 Agent
                agent = DynamicAgentWrapper(
                    initial_tools=tools,
                    model=model_llm_qwen.get_llm(),
                    prompt=hwchase17.get_prompts(user_info,kb_id_t),
                )
                cls._instances[session_id] = agent
            except Exception as e:
                logger.error(f"创建 Agent 失败: {e}")
                raise
        else:
            # Agent 已存在，处理知识库替换和添加临时文件
            agent = cls._instances[session_id]

            # 替换知识库工具
            if kb_ids is not None:
                try:
                    for kb_id in kb_ids:
                        new_kb_tool = get_retriever_tool(kb_id)
                        agent.replace_kb_tool(new_kb_tool)
                except Exception as e:
                    logger.error(f"替换知识库失败: {e}")
        return cls._instances[session_id]


class ChatResource(Resource):
    def post(self):
        data = request.json or {}
        params = self._validate_params(data)
        if isinstance(params, tuple):
            return params

        chat_history = self._load_chat_history(params["session_id"])
        kb_id = params["kb_id"]
        session_id = params["session_id"]
        temp_file_list = params["temp_file_list"]
        user_info = params["user_info"]
        try:
            agent = SingletonAgentManager.get_agent(kb_id, session_id, user_info, temp_file_list)  # 从单例管理器获取
        except Exception as e:
            logger.error(f"加载 Agent 失败: {e}")
            return {"error": "知识库初始化失败"}, 500

        try:
            response = agent.invoke({
                "input": params["input"],
                "chat_history": chat_history
            }, config={"configurable": {"session_id": params["session_id"]}})
        except Exception as e:
            logger.error(f"Agent 处理失败: {e}", exc_info=True)
            return {"error": "服务处理失败"}, 500
        return self._format_response(response, params["session_id"])

    def _validate_params(self, data):
        input_val = data.get("input")
        session_id = data.get("session_id")
        kb_id = data.get("kb_id")
        user_info = data.get("user_info")
        temp_file_list = data.get("temp_file_list")
        for key, value, msg in [
            (input_val, "input", "缺少input参数"),
            (session_id, "session_id", "缺少session_id参数"),
            (user_info, "user_info", "缺少user_info参数"),
        ]:
            if not key:
                return {"error": msg}, 400
        return {"input": input_val,
                "session_id": session_id,
                "kb_id": kb_id,
                "temp_file_list": temp_file_list,
                "user_info": user_info}

    def _load_chat_history(self, session_id):
        data = get_session_server(session_id)
        if not data:
            return []
        history = []
        for msg in data:
            if msg["role"] == "user":
                history.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                history.append(AIMessage(content=msg["content"]))
            elif msg["role"] == "system":
                history.append(SystemMessage(content=msg["content"]))
        return history

    def _format_response(self, response, session_id):
        chat_history = []
        for msg in response.get("chat_history", []):
            role = "user" if isinstance(msg, HumanMessage) else "assistant"
            chat_history.append({"role": role, "content": msg.content})
        return {
            "output": response["output"],
            "session_id": session_id,
            "chat_history": chat_history
        }


class ChatAttachedResource(Resource):
    def post(self):
        file = request.files.get("file")
        session_id = request.form.get("session_id")  # 需要从前端获取session_id

        doc_object = save_doc_server(file, 0, 0)
        doc_id = doc_object[0].get("id")

        kb = get_kb_by_name_server(session_id)
        kb_id = kb[0].get("id")
        add_doc_to_kb_server(kb_id, doc_id)
        if not session_id:
            return {"error": "缺少session_id参数"}, 400

        # 将文件上传动作记录到对话历史
        file_message = f"用户上传了文件: {file.filename}"
        self._record_file_upload(session_id, file_message)

        return {"doc_id": doc_id}, 200

    def delete(self):
        data = request.json or {}
        doc_id = data.get("doc_id")
        session_id = data.get("session_id")  # 需要从前端获取session_id
        doc = get_doc_server(doc_id)
        delete_doc_server(doc_id)
        delete_file_by_url(doc.get("file_path"))
        file_message = f"用户删除了文件: {doc.get('file_name')}"
        self._record_file_upload(session_id, file_message)

    def _record_file_upload(self, session_id, message):
        """记录文件上传到对话历史"""
        # 获取当前会话
        session_data = get_session_server(session_id) or []

        # 添加用户消息
        session_data.append({
            "role": "system",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })

        # 保存回会话存储
        # 这里需要确保您的get_session_server有对应的保存功能
        # 如果没有，您需要实现一个set_session_server函数
        print(add_chat_record_server(session_id, "system", message))

    def _save_session(self, session_id, data):
        """保存会话数据"""
        # 这里需要根据您的实际会话存储方式实现
        # 例如，如果是Redis:
        redis_client.set(f"session:{session_id}", json.dumps(data))
        redis_client.expire(f"session:{session_id}", AGENT_CACHE_TTL)
if __name__ == '__main__':
    print(get_doc_server(1).get("file_name"))