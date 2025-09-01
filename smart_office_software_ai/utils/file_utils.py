import requests
import os
import shutil
from urllib.parse import urlparse


class MockFile:
    def __init__(self, file_path):
        self.file_path = file_path
        self.filename = os.path.basename(urlparse(file_path).path)

    def save(self, temp_path):
        # 检查是否是URL
        if self.file_path.startswith(('http://', 'https://')):
            # 从URL下载文件
            response = requests.get(self.file_path, stream=True)
            response.raise_for_status()  # 检查请求是否成功

            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        else:
            # 处理本地文件
            shutil.copy2(self.file_path, temp_path)


def filename_to_file(file_path):
    return MockFile(file_path)