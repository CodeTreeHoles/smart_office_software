from flask import request
from flask_restful import Resource
import redis
from datetime import timedelta
import logging
from model import model_llm_qwen
from prompts import hwchase17
from server.rag_server import get_retriever_tool
from utils.agent_utils import create_agent_with_knowledge_base
import uuid  # 用于生成唯一ID
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# ========== 初始化 Redis 缓存客户端 ==========
redis_client = redis.Redis(host='localhost', port=6379, db=1)  # 使用独立 DB 1 存储 Agent 缓存


class SingletonAgentManager:
    _instances = {}  # 存储已创建的 Agent

    @classmethod
    def get_agent(cls, kb_id):
        if kb_id not in cls._instances:
            try:
                # 知识库检索工具
                kb_tool = get_retriever_tool(kb_id)
                agent = create_agent_with_knowledge_base(
                    tools=[kb_tool],
                    model=model_llm_qwen.get_llm(),
                    prompt=hwchase17.get_prompts()
                )
                cls._instances[kb_id] = agent
            except Exception as e:
                logger.error(f"创建 Agent 失败: {e}")
                raise
        return cls._instances[kb_id]


class AgentResource(Resource):
    # 维护agent_id到kb_id的映射
    agent_mapping = {}  # 格式: {agent_id: kb_id}

    def post(self):
        data = request.json
        kb_id = data['kb_id']
        try:
            agent = SingletonAgentManager.get_agent(kb_id)
            # 生成唯一的agent_id
            agent_id = str(uuid.uuid4())
            self.agent_mapping[agent_id] = kb_id

            # 将agent_id存入Redis缓存，有效期1小时
            redis_client.setex(f"agent:{agent_id}", timedelta(hours=1), kb_id)

            return {"agent_id": agent_id}, 200
        except Exception as e:
            logger.error(f"加载 Agent 失败: {e}")
            return {"error": "知识库初始化失败"}, 500


class AgentQueryResource(Resource):
    def get(self, agent_id):
        # 先从缓存检查agent_id是否存在
        cached_kb_id = redis_client.get(f"agent:{agent_id}")
        if cached_kb_id:
            kb_id = cached_kb_id.decode('utf-8')
        else:
            # 若缓存失效，检查内存映射（处理短时间内的请求）
            kb_id = AgentResource.agent_mapping.get(agent_id)
            if not kb_id:
                return {"error": "无效的agent_id或已过期"}, 404

        try:
            # 从单例管理器获取Agent（如果存在）
            agent = SingletonAgentManager.get_agent(kb_id)

            # 返回Agent状态信息（可根据需求扩展）
            return {
                "agent_id": agent_id,
                "kb_id": kb_id,
                "status": "active",
                "created_at": redis_client.get(f"agent:{agent_id}:created_at").decode('utf-8') if redis_client.exists(
                    f"agent:{agent_id}:created_at") else None
            }, 200
        except Exception as e:
            logger.error(f"查询 Agent 失败: {e}")
            return {"error": "查询Agent状态失败"}, 500
