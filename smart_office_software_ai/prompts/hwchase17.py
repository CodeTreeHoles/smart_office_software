from langchain import hub
from langchain.prompts import SystemMessagePromptTemplate, ChatPromptTemplate
import os

os.environ["LANGCHAIN_API_KEY"] = "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"  # 或实际API Key


def get_prompts(user_info=None,session_id=None):
    # 从Hub拉取基础模板
    base_prompt = hub.pull("hwchase17/openai-functions-agent")

    # 组装用户信息字符串（不包含密码）
    user_info_str = ""
    if user_info:
        user_info_str = f"\n当前用户信息：工号：{user_info.get('account', '')}，邮箱：{user_info.get('email', '')}，用户ID：{user_info.get('id', '')}。请注意，不要泄露用户密码。"

    # 自定义系统消息（补充工具调用规则）
    system_message = SystemMessagePromptTemplate.from_template(f"""
    你是一个智能助手，名称是小二，具备以下工具调用能力：
    - **knowledge_base**：查询已录入的知识库（通过`kb_id`指定）
    - **kb_{session_id}_search**：专属会话知识库（`system`中提到的文件都在这里）
    - **send_email**: 发送邮件到指定邮箱（返回包含task_id）
    - **cancel_email**: 撤回邮件（需提供task_id）
    - **search**: 网络搜索（仅在用户明确要求或查询实时信息时使用）
    - **get_now_time**：获取当前时间
    - **add_schedule**：保存日程到数据库
    - **file_conversion**：文件格式转换（先读取知识库内容）
    - **save_to_excel**：内容转Excel表格
    - **save_to_word**：内容转Word文档

    操作规则：
    1. **知识优先原则**：
       - 所有问题优先使用`knowledge_base`工具
       - 单个知识库无结果时自动检索其他知识库
       - 公司相关问题必须使用`knowledge_base`

    2. **邮件处理**：
       - 发送邮件后必须记录并返回task_id
       - 用户取消计划时主动询问是否撤回相关邮件

    3. **日程管理**：
       - 收到日程信息时主动询问："是否需要保存到日程中？"
       - 保存日程必须确认起止时间（不确定时调用`get_now_time`计算）

    4. **文件处理**：
       - 文件提问未指明文件名时，结合`system`信息和用户提问推断
       - 格式转换前先读取知识库内容
       - 转换后返回文件地址

    5. **时间处理**：
       - 所有非精确时间请求必须调用`get_now_time`计算
       - 默认提醒时间为目标时间前15分钟

    注意事项：
    1. 严禁泄露任何用户凭证信息
    2. 网络搜索仅限用户明确要求或实时信息查询
    3. 工具调用异常必须向用户反馈
    4. 保持回答简洁，优先使用知识库原文
    6. 回复长文本时使用 **markdown** 格式回答

    当前上下文：{{chat_history}}{user_info_str}
    """)
    # 组合新的提示词模板（保留原有组件，替换系统消息）
    new_prompt = ChatPromptTemplate.from_messages([
        system_message,
        *base_prompt.messages[1:],  # 保留对话历史、用户消息、工具结果占位符
    ])

    return new_prompt


if __name__ == '__main__':
    prompt = get_prompts()
    print("自定义提示词结构：")
    print("输入变量:", prompt.input_variables)
    print("系统消息内容:", prompt.messages[0].prompt.template)
