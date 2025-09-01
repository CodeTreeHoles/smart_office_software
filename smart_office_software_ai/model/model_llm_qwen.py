import os

from dotenv import load_dotenv
from langchain_community.chat_models import ChatTongyi

# llm = ChatOpenAI(
#     openai_api_key="sk-8fee1ef861774ddba9e47d1a75c1ea6e",
#     openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
#     model_name="qwen-plus",
#     model_kwargs={"extra_body": {"enable_thinking": False}}  # 添加模型特定参数
# )
load_dotenv()

api_key = os.getenv('DASHSCOPE_API_KEY')
llm = ChatTongyi(
    model_name="qwen-plus",
    dashscope_api_key=api_key
)


def get_llm():
    return llm


if __name__ == '__main__':
    get_llm()
