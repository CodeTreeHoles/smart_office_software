from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from server.rag_server import *
import redis

# app = Flask(__name__)
# api = Api(app)
#
# # 配置上传文件的临时目录
# UPLOAD_FOLDER = 'temp_uploads'
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

redis_client = redis.Redis(host='localhost', port=6379, db=0)  # 使用独立 DB 1 存储 Agent 缓存


class KnowledgeBaseResource(Resource):
    def get(self):
        kb_id = request.args.get('kb_id')
        result = get_kb_server(kb_id)
        return jsonify(result)

    def post(self):
        """创建知识库"""
        data = request.get_json()
        kb_name = data.get('kb_name')
        description = data.get('description')
        dept_id = data.get('dept_id')
        if not kb_name:
            return {'error': '知识库名称不能为空'}, 400

        try:
            kb_id = create_kb_server(kb_name, description)
            save_kb_dept_server(kb_id, dept_id)
            return {'message': '知识库创建成功', 'kb_id': kb_id}, 201
        except Exception as e:
            return {'error': f'创建失败: {str(e)}'}, 500

    def put(self):
        """更新知识库(描述信息)"""
        data = request.get_json()
        kb_id = data.get('kb_id')
        kb_name = data.get('kb_name')
        img = data.get('img')
        description = data.get('description')

        if not kb_id:
            return {'error': '必须提供 kb_id'}, 400

        try:
            result = update_kb_server(kb_name, description, kb_id, img)
            if result > 0:
                return {'message': '知识库更新成功'}, 200
            else:
                return {'message': '未找到对应的知识库'}, 404
        except Exception as e:
            return {'error': f'更新失败: {str(e)}'}, 500

    def delete(self):
        """删除知识库"""
        kb_id = request.get_json().get('kb_id')

        if not kb_id:
            return {'error': '必须提供 kb_id'}, 400

        try:
            if delete_kb_server(kb_id) == False:
                return {'message': '公共知识库无法删除'}
            return {'message': '删除成功'}
        except Exception as e:
            return {'error': f'删除失败: {str(e)}'}, 500


class KnowledgeBaseToDocumentsResource(Resource):
    def get(self):
        kb_id = request.args.get('kb_id')
        return jsonify(get_doc_by_kb_id_server(kb_id))

    # 将一个文档加载到指定的知识库中
    def post(self):
        data = request.get_json()
        kb_id = data.get('kb_id')
        document_id = data.get('doc_id')
        add_doc_to_kb_server(kb_id, document_id)

    def delete(self):
        data = request.get_json()
        kb_id = data.get('kb_id')
        doc_id = data.get('doc_id')
        delete_doc_from_kb_server(kb_id, doc_id)
        return {'message': '删除成功'}


class KnowledgeBaseListResource(Resource):
    # 获取所有的知识库信息
    def get(self):
        user_id = request.args.get('user_id')
        return jsonify(dept_kb_list_server(user_id))


class PublicKnowledgeBaseResource(Resource):
    def get(self):
        code = request.args.get('code')
        role = redis_client.get(code)
        if role == b'0':
            print(1)
            public_kb = get_public_kb_server()[0]
            return jsonify(public_kb)
        else:
            return {"message": "用户无权限"}, 500
