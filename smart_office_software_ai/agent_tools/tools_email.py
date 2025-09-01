import configparser
import os
import uuid
import redis
import requests
import json
from datetime import datetime
from langchain.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

from server.rabbitMQ_server import send_delayed_message

try:
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(os.path.dirname(script_path))+'\\'+'config\\config.ini'
    # 读取配置
    config = configparser.ConfigParser()
    config.read(script_dir, encoding='utf-8')
    # url_base = config.get('email', 'url_base')
    url_base = "http://127.0.0.1:8080"
    url_send = url_base + "/email/send"
    url_cancel = url_base + "/email/cancel"
except Exception as e:
    raise Exception(f"配置读取失败: {e}")

# Redis配置
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
REDIS_DB = int(os.environ.get('REDIS_DB', 0))

# 创建Redis客户端
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB
)
class SendEmailInput(BaseModel):
    email: str = Field(..., description="目标的邮箱号")
    subject: str = Field(..., description="邮件的主题")
    message: str = Field(..., description="邮件的内容")
    send_time: str = Field(..., description="指定送达时间，格式必须为 'yyyy-MM-dd HH:mm:ss'")


def send_email(email: str, subject: str, message: str, send_time: str) -> str:
    """
    发送一个邮件到指定的邮箱，当时间到达send_time时会发送邮件
    Args:
        email: 目标的邮箱号
        subject: 邮件的主题
        message: 邮件的内容
        send_time: 指定送达时间，格式必须为 'yyyy-MM-dd HH:mm:ss'
    Returns:
        返回的是一个task_id,即任务id，通过它我们可以撤回一个邮箱发送
    Raises:
        ValueError: 当send_time格式不符合要求时抛出
        Exception: 处理请求异常和配置错误
    """
    # 验证send_time格式
    try:
        target_time = datetime.strptime(send_time, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        raise ValueError("send_time参数格式错误，需要'yyyy-MM-dd HH:mm:ss'格式")
    # 获取当前时间
    current_time = datetime.now()

    # 计算时间差
    time_delta = target_time - current_time

    # 将时间差转换为毫秒
    milliseconds = int(time_delta.total_seconds() * 1000)
    milliseconds = max(milliseconds,0)
    task_id = uuid.uuid4().hex
    # 表单参数
    data = {
        "subject": subject,
        "email": email,
        "content": message,
        "taskId": task_id
    }

    try:
        redis_client.set(task_id, json.dumps(subject))
        send_delayed_message(data, milliseconds)
        return task_id
    except requests.exceptions.RequestException as e:
        raise Exception(f"邮件发送请求失败: {e}")
    except json.JSONDecodeError:
        raise Exception("响应解析失败，返回内容不是有效的JSON格式")


def cancel_email(task_id: str) -> str:
    """
    Args:
        task_id: 邮件发送任务的ID
    Returns:
        返回一个dict对象，是响应数据的json解析结果。
        'code':0说明响应正常，已经取消了邮箱发送任务。
        'code':1说明出现了异常，取消失败。
    """
    redis_client.delete(task_id)
    return "成功撤回邮件"


# 创建结构化工具 - 添加类型注解
class SendEmailTool(BaseTool):
    name: str = "send_email"
    description: str = "发送一个邮件到指定的邮箱，当时间到达send_time时会发送邮件"
    args_schema: Type[BaseModel] = SendEmailInput

    def _run(self, email: str, subject: str, message: str, send_time: str) -> str:
        return send_email(email, subject, message, send_time)

    def _arun(self, email: str, subject: str, message: str, send_time: str) -> str:
        raise NotImplementedError("send_email不支持异步调用")


# 保持cancel_email工具不变 - 添加类型注解
class CancelEmailTool(BaseTool):
    name: str = "cancel_email"
    description: str = "通过task_id删除指定的邮箱发送任务"

    def _run(self, task_id: str) -> str:
        return cancel_email(task_id)

    def _arun(self, task_id: str) -> str:
        raise NotImplementedError("cancel_email不支持异步调用")


def get_all_email_tools():
    send_tool = SendEmailTool()
    cancel_tool = CancelEmailTool()
    tools = [send_tool, cancel_tool]
    return tools
