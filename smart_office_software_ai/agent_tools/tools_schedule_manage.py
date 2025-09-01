from typing import Type

from langchain_core.tools import BaseTool

from server.rabbitMQ_server import send_message
from pydantic import BaseModel, Field


class ScheduleModel(BaseModel):
    user_id: int = Field(..., description="用户id")
    event_name: str = Field(..., description="事件名称")
    start_time: str = Field(..., description="开始时间，格式必须为 'yyyy-MM-dd HH:mm:ss'")
    end_time: str = Field(..., description="结束时间，格式必须为 'yyyy-MM-dd HH:mm:ss'")
    description: str = Field(..., description="事件的描述性信息")


def add_schedule(user_id: int, event_name: str, start_time: str, end_time: str, description: str):
    """
    添加一个新的日程，需要用到用户id
    Args:
        user_id (int): 用户id
        event_name (str): 事件名称
        start_time (str): 开始时间
        end_time (str): 结束时间
        description (str): 事件的描述性信息，内容简短
    """
    data = {
        "task": "addSchedule",
        "schedule": {
            "userId": user_id,
            "eventName": event_name,
            "startTime": start_time,
            "endTime": end_time,
            "description": description
        }
    }
    send_message(data)


class ScheduleManageTool(BaseTool):
    name: str = "add_schedule"
    description: str = "将编辑好的日程保存起来，描述信息为地点或时间、目的"
    args_schema: Type[BaseModel] = ScheduleModel

    def _run(self, user_id: int, event_name: str, start_time: str, end_time: str, description: str):
        add_schedule(user_id, event_name, start_time, end_time, description)


def get_all_schedule_tools():
    schedule_manage = ScheduleManageTool()
    return schedule_manage
