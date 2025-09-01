import os
import datetime

import oss2
from dotenv import load_dotenv
from oss2 import Auth, Bucket
from urllib.parse import urlparse, unquote

# 加载环境变量
load_dotenv()

# OSS配置信息
# 阿里云官网申请
OSS_ACCESS_KEY_ID = os.environ.get('OSS_ACCESS_KEY_ID')
OSS_ACCESS_KEY_SECRET = os.environ.get('OSS_ACCESS_KEY_SECRET')
OSS_ENDPOINT = os.environ.get('OSS_ENDPOINT')
OSS_BUCKET_NAME = os.environ.get('OSS_BUCKET_NAME')
OSS_IS_PRIVATE = True  # 设为True表示Bucket是私有权限，需生成签名URL

# 初始化OSS Bucket
auth = Auth(OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET)
bucket = Bucket(auth, OSS_ENDPOINT, OSS_BUCKET_NAME)


def save_file(file, folder_path=''):
    """
    上传文件到OSS的指定文件夹并返回访问URL
    :param file: 上传的文件对象（如Flask的request.files中的文件）
    :param folder_path: 要保存到的文件夹路径（如 'user_uploads/'），默认为根目录
    :return: 包含操作结果、文件URL和元信息的字典
    """
    # 处理文件夹路径
    folder_path = folder_path.strip('/')  # 移除首尾斜杠
    if folder_path and not folder_path.endswith('/'):
        folder_path += '/'

    # 处理原始文件名
    file_name = file.filename
    base_name, ext = os.path.splitext(file_name)
    file_ext = ext if ext.startswith('.') else f'.{ext}' if ext else ''

    # 生成唯一文件名（原始文件名+时间戳）
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]
    unique_filename = f"{base_name}_{timestamp}{file_ext}"

    # 组合完整OSS路径
    oss_key = f"{folder_path}{unique_filename}"

    try:
        # 上传文件到OSS
        result = bucket.put_object(oss_key, file.stream)

        if result.status == 200:
            # 根据Bucket权限生成不同类型的URL
            if OSS_IS_PRIVATE:
                # 私有Bucket生成带签名的临时URL（有效期1小时）
                file_url = bucket.sign_url('GET', oss_key, 3600)
            else:
                # 公共Bucket生成直接访问URL
                file_url = f"https://{OSS_BUCKET_NAME}.{OSS_ENDPOINT.replace('http://', '')}/{oss_key}"

            # 构建文件元信息
            doc_info = {
                'file_name': file_name,
                'oss_key': oss_key,
                'content_type': file.content_type,
                'create_time': datetime.datetime.now(),
                'url': file_url,
                'folder_path': folder_path
            }

            return {
                'success': True,
                'url': file_url,
                'doc_info': doc_info,
                'message': '文件上传成功'
            }
        else:
            return {
                'success': False,
                'error': f'OSS上传失败，状态码: {result.status}',
                'status_code': result.status
            }
    except Exception as e:
        return {
            'success': False,
            'error': f'上传异常: {str(e)}',
            'exception_type': type(e).__name__
        }


def delete_file_by_url(file_url):
    """
    从OSS删除指定URL对应的文件（自动解码URL路径）
    :param file_url: OSS文件的完整URL
    :return: 包含操作结果的字典
    """
    try:
        # 解析URL
        parsed_url = urlparse(file_url)
        # 解码路径并移除开头斜杠
        encoded_path = parsed_url.path.lstrip('/')
        oss_key = unquote(encoded_path)  # 关键修改：解码URL路径

        # 验证Bucket一致性
        expected_bucket = OSS_BUCKET_NAME
        if expected_bucket not in parsed_url.netloc:
            return {
                'success': False,
                'error': f'URL所属Bucket({parsed_url.netloc})与配置不一致({expected_bucket})',
                'status_code': 400
            }

        # 检查文件是否存在
        exists = bucket.object_exists(oss_key)
        if not exists:
            return {
                'success': False,
                'error': f'文件不存在: {oss_key}',
                'status_code': 404
            }

        # 删除文件
        result = bucket.delete_object(oss_key)

        if result.status == 204:
            return {
                'success': True,
                'message': f'文件删除成功: {oss_key}'
            }
        else:
            # 获取OSS错误详情（适用于oss2 >= 2.16.0）
            error_info = ""
            if hasattr(result, 'error'):
                error_info = f", 错误信息: {result.error}"

            return {
                'success': False,
                'error': f'OSS删除失败，状态码: {result.status}{error_info}',
                'status_code': result.status
            }
    except oss2.exceptions.OssError as oe:
        # 专门处理OSS客户端异常
        return {
            'success': False,
            'error': f'OSS操作异常: {oe}',
            'oss_error_code': getattr(oe, 'error_code', '未知'),
            'status_code': oe.status_code if hasattr(oe, 'status_code') else 500
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'删除异常: {str(e)}',
            'exception_type': type(e).__name__
        }


def delete_folder_from_oss(folder_prefix):
    """
    删除OSS上的指定文件夹及其所有内容
    :param folder_prefix: 要删除的文件夹前缀（如 'images/'）
    :return: 包含操作结果的字典
    """
    if not folder_prefix.endswith('/'):
        folder_prefix += '/'

    deleted_files = []
    try:
        # 列出文件夹下的所有文件
        for obj in oss2.ObjectIterator(bucket, prefix=folder_prefix):
            # 删除文件
            result = bucket.delete_object(obj.key)

            if result.status == 204:
                deleted_files.append(obj.key)
            else:
                return {
                    'success': False,
                    'error': f'文件 {obj.key} 删除失败，状态码: {result.status}',
                    'status_code': result.status,
                    'deleted_files': deleted_files
                }

        return {
            'success': True,
            'message': f'文件夹删除成功，共删除 {len(deleted_files)} 个文件',
            'deleted_files': deleted_files,
            'total_deleted': len(deleted_files)
        }

    except oss2.exceptions.OssError as oe:
        return {
            'success': False,
            'error': f'OSS操作异常: {oe}',
            'oss_error_code': getattr(oe, 'error_code', '未知'),
            'status_code': oe.status_code if hasattr(oe, 'status_code') else 500
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'文件夹删除异常: {str(e)}',
            'exception_type': type(e).__name__
        }


if __name__ == '__main__':
    file = "https://rag-temp.oss-cn-hangzhou.aliyuncs.com/%E6%96%B0%E5%BB%BA%20Microsoft%20Excel%20%E5%B7%A5%E4%BD%9C%E8%A1%A8_20250630171810537.xlsx"
    print(delete_file_by_url(file))