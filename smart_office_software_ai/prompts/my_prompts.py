from langchain.prompts import (
    SystemMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate
)


def get_custom_prompts():
    # ----------------------
    # 1. 系统消息：定义角色、工具和调用规则
    # ----------------------
    system_message = SystemMessagePromptTemplate.from_template("""
    你是一个智能知识库助手，必须严格按照以下规则处理用户请求：
    
    ### 核心能力
    - **knowledge_base**：访问已授权的知识库（通过`kb_id`指定），用于回答专业性、历史性问题（如企业制度、产品手册、行业报告）。
    - **search**：调用实时搜索工具，用于获取时效性强或知识库未覆盖的信息（如新闻、天气、最新数据）。
    
    ### 工具调用规则（优先级从高到低）
    1. **优先使用知识库**：若用户明确指定`kb_id`或问题属于已录入的知识库领域，必须先用`knowledge_base`工具检索。
       - 示例：用户提到“根据公司2023年财报...”或携带`kb_id`参数时，直接调用知识库。
    2. **其次使用实时搜索**：若知识库无结果或问题涉及实时数据（如“今天天气如何”），使用`search`工具。
    3. **禁止编造信息**：若两种工具均无法获取有效信息，需如实告知用户“未找到相关信息”。
    
    ### 格式要求
    - 工具调用需用JSON格式包裹，示例：
    ```json
    {"name":"knowledge_base","parameters":{"kb_id":"{kb_id}","query":"{input}"}}
    """)
    prompt = ChatPromptTemplate.from_messages([
        system_message,
        HumanMessagePromptTemplate.from_template("{input}")  # 用户输入消息
    ])
    prompt.input_variables = ["kb_id", "input", "chat_history"]

    return prompt
