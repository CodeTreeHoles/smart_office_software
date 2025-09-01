import os

from resource.agent_resource import *
from resource.session_resource import *
from resource.vector_resource import *  # 从包中导入资源类
from resource.knowledge_base_resource import *
from resource.chat_resource import *
app = Flask(__name__)
api = Api(app)

# 配置上传文件的临时目录
UPLOAD_FOLDER = 'temp_uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 注册路由
api.add_resource(KnowledgeBaseResource, '/knowledge_base')
api.add_resource(KnowledgeBaseListResource, '/knowledge_base/dept_id/list')
api.add_resource(PublicKnowledgeBaseResource, '/knowledge_base/public')
api.add_resource(KnowledgeBaseToDocumentsResource, '/knowledge_base/doc')
api.add_resource(VectorResource, '/vector')
api.add_resource(ChatResource, '/chat')
api.add_resource(AgentResource, '/agent')
api.add_resource(AgentQueryResource, '/agent/<string:agent_id>')
api.add_resource(SessionListResource, '/session/list/<string:user_id>')
api.add_resource(DeleteSessionResource, '/session/<string:session_id>')
api.add_resource(SessionResource, '/session')
api.add_resource(ChatHistoryResource, '/session/record/<string:session_id>')
api.add_resource(ChatAttachedResource, '/chat/attached')

# 根路径返回API信息
@app.route('/')
def index():
    return {'message': 'RAG 知识库 API 服务', 'version': '1.0.0', 'documentation': 'https://your-documentation-url.com'}


# 自定义错误处理
@app.errorhandler(404)
def not_found(error):
    return {'error': '未找到该资源'}, 404


@app.errorhandler(500)
def internal_error(error):
    return {'error': '服务器内部错误，请稍后再试'}, 500
