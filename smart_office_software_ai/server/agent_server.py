from agent_tools.tools_email import get_all_email_tools
from agent_tools.tools_schedule_manage import get_all_schedule_tools
from agent_tools.tools_tavily import get_search
from agent_tools.tools_time import create_time_tool
from agent_tools.tools_to_word import get_word_tools
from agent_tools.tools_to_xlsx import get_excel_tools
from server.rag_server import get_retriever_tool, get_kb_by_name_server, get_kb_server, get_public_kb_server


def public_tools(kb_id_t):
    # 转换输出excel表格
    excel_save_tools = get_excel_tools()
    # 转换输出word文档
    word_save_tools = get_word_tools()
    # 对应会话的临时知识库
    kb_t_tools = get_retriever_tool(kb_id_t)
    # 邮箱工具
    email_tools = get_all_email_tools()
    # 公用知识库
    public_kb = get_public_kb_server()[0]
    public_kb_tool = get_retriever_tool(public_kb.get("id"))
    # 日程管理工具
    schedule_tools = get_all_schedule_tools()
    # 时间工具
    time_tool = create_time_tool()
    # 搜索工具
    search = get_search()
    tools = [email_tools[0], email_tools[1], time_tool, search, schedule_tools, kb_t_tools,
             public_kb_tool,excel_save_tools, word_save_tools]
    return tools
