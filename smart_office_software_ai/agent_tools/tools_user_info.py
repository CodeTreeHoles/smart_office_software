from langchain.tools import StructuredTool


def create_user_info_tool(user_info):
    """根据用户 ID 创建特定的工具"""

    def get_user_info():
        return user_info

    # 创建并返回用户特定的工具
    return StructuredTool.from_function(
        name=f"get_user_info",
        func=get_user_info,
        description=f"获取用户的信息"
    )