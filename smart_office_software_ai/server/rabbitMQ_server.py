import json
import time
import pika
import os
import redis
from dotenv import load_dotenv
from singleton_decorator import singleton

# 加载环境变量
load_dotenv()

# RabbitMQ配置
RABBITMQ_USER = os.environ.get('RABBITMQ_USER')
RABBITMQ_PASSWORD = os.environ.get('RABBITMQ_PASSWORD')
RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST')
RABBITMQ_PORT = int(os.environ.get('RABBITMQ_PORT', 5672))
DELAYED_EXCHANGE_NAME = os.environ.get('DELAYED_EMAIL_EXCHANGE', 'delayed_email_exchange')
DELAYED_QUEUE_NAME = os.environ.get('DELAYED_EMAIL_QUEUE', 'delayed_email_queue')
NORMAL_EXCHANGE = os.environ.get('NORMAL_EXCHANGE', 'normal_exchange')
TASK_NOTIFICATION_QUEUE = os.environ.get('TASK_NOTIFICATION_QUEUE', 'task_notification_queue')
# Redis配置
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
REDIS_DB = int(os.environ.get('REDIS_DB', 0))

# 创建Redis客户端（单例）
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB
)


# RabbitMQ连接单例
@singleton
class RabbitMQConnection:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.initialized = False

    def initialize(self):
        """初始化RabbitMQ连接和通道"""
        try:
            credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
            params = pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                port=RABBITMQ_PORT,
                credentials=credentials,
                heartbeat=60,  # 降低心跳频率
                blocked_connection_timeout=300
            )
            self.connection = pika.BlockingConnection(params)
            self.channel = self.connection.channel()

            # 声明延迟交换和队列（仅初始化时执行一次）
            self.channel.exchange_declare(
                exchange=DELAYED_EXCHANGE_NAME,
                exchange_type='x-delayed-message',
                durable=True,
                arguments={'x-delayed-type': 'direct'}
            )
            self.channel.queue_declare(queue=DELAYED_QUEUE_NAME, durable=True)
            self.channel.queue_bind(
                queue=DELAYED_QUEUE_NAME,
                exchange=DELAYED_EXCHANGE_NAME,
                routing_key=DELAYED_QUEUE_NAME
            )
            self.initialized = True
            print("RabbitMQ连接初始化成功")
        except Exception as e:
            print(f"RabbitMQ初始化失败: {e}")
            raise

    def get_channel(self):
        """获取通道（确保连接已初始化）"""
        if not self.initialized:
            self.initialize()
        return self.channel

    def close(self):
        """关闭连接（仅在程序退出时调用）"""
        if self.channel and self.channel.is_open:
            self.channel.close()
        if self.connection and self.connection.is_open:
            self.connection.close()
            print("RabbitMQ连接已正常关闭")
        self.initialized = False


def send_message(message):
    rabbitmq = RabbitMQConnection()
    channel = rabbitmq.get_channel()

    # 声明常规交换机和队列
    channel.exchange_declare(
        exchange=NORMAL_EXCHANGE,
        exchange_type='direct',  # 假设使用direct类型，可根据需求修改
        durable=True
    )
    channel.queue_declare(queue=TASK_NOTIFICATION_QUEUE, durable=True)
    channel.queue_bind(
        queue=TASK_NOTIFICATION_QUEUE,
        exchange=NORMAL_EXCHANGE,
        routing_key=TASK_NOTIFICATION_QUEUE
    )

    try:
        # 启用发布确认
        channel.confirm_delivery()

        # 构建消息属性
        properties = pika.BasicProperties(
            delivery_mode=2,  # 持久化消息
            content_type='application/json'
        )

        # 发送消息并确认
        channel.basic_publish(
            exchange=NORMAL_EXCHANGE,
            routing_key=TASK_NOTIFICATION_QUEUE,
            body=json.dumps(message),
            properties=properties,
            mandatory=True  # 强制标志，确保消息不会丢失
        )
        print(f"消息发送成功: {message.get('taskId')}")
        return True
    except pika.exceptions.UnroutableError:
        print("错误: 消息无法路由到队列")
        return False
    except pika.exceptions.AMQPConnectionError as e:
        print(f"RabbitMQ连接异常: {e}，尝试重新连接...")
        RabbitMQConnection().close()  # 关闭旧连接
        return send_message(message)  # 重试
    except Exception as e:
        print(f"发送消息失败: {e}")
        return False


def send_delayed_message(message, delay_ms=0):
    """发送延迟消息（使用单例连接）"""
    try:
        # 获取单例连接的通道
        rabbitmq = RabbitMQConnection()
        channel = rabbitmq.get_channel()

        # 构建消息属性
        properties = pika.BasicProperties(
            delivery_mode=2,  # 持久化消息
            content_type='application/json'
        )

        # 设置延迟
        if delay_ms > 0:
            properties = pika.BasicProperties(
                delivery_mode=2,
                content_type='application/json',
                headers={'x-delay': delay_ms}
            )

        # 发送消息
        channel.basic_publish(
            exchange=DELAYED_EXCHANGE_NAME,
            routing_key=DELAYED_QUEUE_NAME,
            body=json.dumps(message),
            properties=properties
        )
        return True
    except pika.exceptions.AMQPConnectionError as e:
        print(f"RabbitMQ连接异常: {e}，尝试重新连接...")
        # 连接异常时重新初始化
        RabbitMQConnection().close()  # 先关闭旧连接
        return send_delayed_message(message, delay_ms)  # 重试
    except Exception as e:
        print(f"发送消息失败: {e}")
        raise


if __name__ == '__main__':
    # 测试示例
    task = "addSchedule"

    test_message = {
        "task": task,
        "schedule": {
            "userId": 1,
            "eventName": "开会",
            "startTime": "2025-06-23 16:20:00",
            "endTime": "2025-06-23 17:20:00",
            "description": "一个非常重要的会议"
        }
    }
    send_message(test_message)
