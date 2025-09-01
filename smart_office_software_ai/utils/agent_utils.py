from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.messages import HumanMessage, AIMessage
from agent_tools.tools_email import *
redis_client = redis.Redis(host='localhost', port=6379, db=0)


def create_agent_with_knowledge_base(tools, model, prompt):
    # 创建一个 agent
    agent = create_tool_calling_agent(model, tools, prompt)
    # 执行 agent
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return agent_executor


def load_chat_history(chat_history_data):
    chat_history = []
    if chat_history_data:
        history_messages = json.loads(chat_history_data)
        for msg in history_messages:
            if msg['role'] == 'user':
                chat_history.append(HumanMessage(content=msg['content']))
            elif msg['role'] == 'assistant':
                chat_history.append(AIMessage(content=msg['content']))
    return chat_history


class DynamicAgentWrapper:
    def __init__(self, initial_tools, model, prompt):
        self._tools = initial_tools
        self._model = model
        self._prompt = prompt
        self._agent_executor = self._create_agent_executor()

    def _create_agent_executor(self):
        return create_agent_with_knowledge_base(
            tools=self._tools,
            model=self._model,
            prompt=self._prompt,
        )

    def replace_kb_tool(self, new_kb_tool):
        """替换知识库工具，如果存在则替换，否则添加"""
        # 使用 "kb_{kb_id}_search" 格式匹配知识库工具
        kb_tool_prefix = "kb_"
        kb_tool_suffix = "_search"

        if kb_tool_prefix in new_kb_tool.name and new_kb_tool.name.endswith(kb_tool_suffix):
            # 查找并替换已存在的知识库工具
            for i, tool in enumerate(self._tools):
                if (kb_tool_prefix in tool.name and tool.name.endswith(kb_tool_suffix)
                        and tool.name != "kb_2_search"):  # 不替换公共知识库
                    self._tools[i] = new_kb_tool
                    self._agent_executor = self._create_agent_executor()
                    return True
            # 如果没有找到，则添加新工具
            self.add_tool(new_kb_tool)
            return True
        else:
            return False
    def add_tool(self, tool):
        # 避免添加重复工具
        if not any(t.name == tool.name for t in self._tools):
            self._tools.append(tool)
            self._agent_executor = self._create_agent_executor()

    def __getattr__(self, attr):
        # 将其他方法调用代理到 AgentExecutor
        return getattr(self._agent_executor, attr)