import time
from langchain.agents import Tool
from langchain.tools import StructuredTool


def create_time_tool():
    """用于获取当前时间"""

    def get_now_time():
        """用于获取当前时间"""
        return time.strftime("%Y-%m-%d %H:%M:%S %A", time.localtime())

    return StructuredTool.from_function(
        name=f"get_now_time",
        func=get_now_time,
        description="获取当前的时间"
    )