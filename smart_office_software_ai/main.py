import argparse

from dotenv import load_dotenv

# 从app.py导入Flask应用实例
from app import app
from flask_cors import CORS  # 导入 CORS 模块
# 允许所有来源的跨域请求（开发环境适用）
CORS(app, resources={r"*": {"origins": "*"}})
if __name__ == '__main__':
    # 加载环境变量
    load_dotenv()

    parser = argparse.ArgumentParser(description='RAG 知识库 API 服务')
    parser.add_argument('--host', default='0.0.0.0', help='服务器监听地址')
    parser.add_argument('--port', type=int, default=5000, help='服务器监听端口')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')

    args = parser.parse_args()

    print(f"服务器将运行在 http://{args.host}:{args.port}")
    if args.debug:
        print("调试模式已启用")

    # 启动应用
    app.run(host=args.host, port=args.port, debug=args.debug)