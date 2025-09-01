import os
import uuid
from datetime import datetime

from db.doc_db import *
from db.doc_kb_db import delete_doc_kb_by_doc_id
from db.kb_db import delete_text_chunks
from utils.oss_utils import save_file


def get_doc_server(document_id):
    result = get_doc_db(document_id)
    return result


def save_doc_server(file, user_id=0, scope=0):
    data = save_file(file)
    file_url = data['url']
    file_name = file.filename
    file_type = os.path.splitext(file_name)[1].lower()[1:]
    save_doc_db(file_url, file_name, user_id, scope, file_type)
    return get_doc_by_path_db(file_url)


def delete_doc_server(document_id):
    delete_doc_kb_by_doc_id(document_id)
    delete_doc_db(document_id)
    delete_text_chunks(document_id)
