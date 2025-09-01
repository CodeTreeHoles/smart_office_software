from flask import request
from flask_restful import Resource
from server.doc_server import get_doc_server
from server.rag_server import *
from utils.file_utils import filename_to_file


class VectorResource(Resource):
    def post(self):
        """
            将指定的文档转换为向量存储在数据库中
        """
        data = request.get_json()
        document_id = data.get('document_id')
        doc = get_doc_server(document_id)
        if doc is None:
            return {'error': '没有找到该文件'}, 400
        try:
            file = filename_to_file(doc.get("file_path"))
            save_doc_to_vector_server(file, document_id)
            return {'success': True}, 200
        except Exception as e:
            return {'error': f'向量化过程中出现了问题: {str(e)}'}, 500

# 注册路由
# api.add_resource(VectorResource, '/vector')
