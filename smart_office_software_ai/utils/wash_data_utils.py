import pandas as pd
import docx
import re
import os
import pdfplumber
import requests
from urllib.parse import urlparse
import shutil

# 配置固定的下载目录和输出目录（使用项目内相对路径）
DOWNLOAD_DIR = "downloaded_files"
OUTPUT_DIR = "../cleaned_files"  # 保持原有保存位置不变


def clean_data_file(input_file_path, output_file_path=None):
    """
    数据清洗函数，将所有类型的文件统一输出为TXT格式，返回指定格式的绝对路径

    参数:
        input_file_path (str): 输入文件路径，可以是本地路径或URL
        output_file_path (str, 可选): 输出文件路径，如果为None则自动生成

    支持的文件类型:
        - PDF (.pdf)
        - DOCX (.docx)
        - CSV (.csv)
        - TXT (.txt)

    返回:
        str: 输出文件的绝对路径
    """

    def is_url(path):
        """判断路径是否为URL"""
        return path.startswith(('http://', 'https://'))

    def download_file(url):
        """从URL下载文件到固定目录"""
        try:
            os.makedirs(DOWNLOAD_DIR, exist_ok=True)
            url_path = urlparse(url).path
            filename = os.path.basename(url_path) or f"file_{hash(url) & 0xfffffff}.tmp"
            download_path = os.path.join(DOWNLOAD_DIR, filename)
            response = requests.get(url, stream=True)
            response.raise_for_status()
            with open(download_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            # 转换为绝对路径并规范路径分隔符
            abs_download_path = os.path.abspath(download_path)
            return abs_download_path
        except Exception as e:
            raise IOError(f"下载文件时出错: {e}")

    def clean_text(text):
        """清洗文本数据"""
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s.,!?;:()（）\-_]+', '', text)
        text = re.sub(r'([.,!?;:])\1+', r'\1', text)
        return text

    def process_csv(file_path):
        """处理CSV文件并返回清洗后的文本"""
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='gbk', on_bad_lines='skip')
        text_content = "\n".join([f"{col}: {', '.join(str(x) for x in df[col].tolist())}" for col in df.columns])
        return clean_text(text_content)

    def process_doc(file_path):
        pass

    def process_txt(file_path):
        """处理TXT文件并返回清洗后的内容"""
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        return clean_text(content) if content else ""

    def process_pdf(file_path):
        """使用pdfplumber处理PDF文件，返回清洗后的文本"""
        with pdfplumber.open(file_path) as pdf:
            text_content = "\n".join([page.extract_text() or "" for page in pdf.pages])
        return clean_text(text_content)

    def process_docx(file_path):
        """处理DOCX文件并返回清洗后的文本"""
        doc = docx.Document(file_path)
        text_content = "\n".join([para.text for para in doc.paragraphs if para.text])
        return clean_text(text_content)

    # 确保输出目录存在，并转换为绝对路径
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    abs_output_dir = os.path.abspath(OUTPUT_DIR)

    input_is_downloaded = False
    original_file_path = input_file_path

    try:
        if is_url(input_file_path):
            input_file_path = download_file(input_file_path)
            input_is_downloaded = True

        file_ext = input_file_path.rsplit('.', 1)[1].lower()
        if file_ext not in {'pdf', 'docx', 'csv', 'txt', 'doc', 'xlsx'}:
            raise ValueError(f"不支持的文件类型: {file_ext}，支持类型: pdf, docx, csv, txt, doc, xlsx")

        # 提取文件名（不包含扩展名）
        base_name = os.path.splitext(os.path.basename(input_file_path))[0]

        # 生成绝对路径的输出文件
        if output_file_path is None:
            final_output = os.path.join(abs_output_dir, f"{base_name}_cleaned.txt")
        else:
            # 确保用户指定的路径符合格式要求
            custom_base = os.path.splitext(os.path.basename(output_file_path))[0]
            final_output = os.path.join(abs_output_dir, f"{custom_base}_cleaned.txt")

        # 执行数据清洗
        if file_ext == 'csv':
            cleaned_content = process_csv(input_file_path)
        elif file_ext == 'txt':
            cleaned_content = process_txt(input_file_path)
        elif file_ext == 'pdf':
            cleaned_content = process_pdf(input_file_path)
        elif file_ext == 'docx':
            cleaned_content = process_docx(input_file_path)
        elif file_ext == 'doc':
            return original_file_path
        elif file_ext == 'xlsx':
            return original_file_path

        with open(final_output, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)

        # 转换为绝对路径并规范路径分隔符
        actual_save_path = os.path.abspath(final_output)

        return actual_save_path

    except Exception as e:
        return None

    finally:
        if input_is_downloaded and os.path.exists(input_file_path):
            try:
                # 转换为相对路径并规范路径分隔符
                rel_temp_path = os.path.relpath(input_file_path)
                os.remove(input_file_path)
                print(f"已删除临时文件: {rel_temp_path}")
            except:
                pass


# 使用示例
if __name__ == "__main__":
    print("数据清洗工具启动，输出路径格式为绝对路径")
    sample_url = "http://rag-temp.oss-cn-hangzhou.aliyuncs.com/%E6%96%B0%E5%BB%BA%20Microsoft%20Excel%20%E5%B7%A5%E4%BD%9C%E8%A1%A8_20250630161805205.xlsx?OSSAccessKeyId=LTAI5tAvvRvC49NnVRpwUN5U&Expires=1751275085&Signature=fJmlgnEh1lbstoxqrJVDZ9kmzC8%3D"
    result_path = clean_data_file(sample_url)
    # if result_path:
    print(f"清洗结果路径: {result_path}")
