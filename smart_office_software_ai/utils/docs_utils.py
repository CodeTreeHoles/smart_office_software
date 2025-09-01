import os
import tempfile
import shutil
import chardet
import subprocess


def load_docs(file):
    """从上传的文件中加载文档内容"""
    # 获取文件名和扩展名
    filename = file.filename
    if not filename:
        raise ValueError("无效的文件名")

    # 获取文件扩展名，确定加载器类型
    ext = os.path.splitext(filename)[1].lower()

    # 保存临时文件
    temp_file_path = os.path.join(tempfile.gettempdir(), filename)
    file.save(temp_file_path)

    try:
        # 根据文件类型选择合适的加载器
        if ext == '.pdf':
            from langchain_community.document_loaders import PyPDFLoader
            loader = PyPDFLoader(temp_file_path)
        elif ext == '.docx':
            from langchain_community.document_loaders import Docx2txtLoader
            loader = Docx2txtLoader(temp_file_path)
        elif ext == '.doc':
            # 创建临时docx文件路径
            docx_temp_file_path = os.path.splitext(temp_file_path)[0] + '.docx'

            # 尝试使用python-docx将doc转换为docx
            try:
                # 检查操作系统类型
                if os.name == 'nt':  # Windows系统
                    # 使用win32com（需要安装pywin32）
                    import win32com.client
                    word = win32com.client.Dispatch("Word.Application")
                    doc = word.Documents.Open(temp_file_path)
                    doc.SaveAs(docx_temp_file_path, FileFormat=16)  # 16 = docx
                    doc.Close()
                    word.Quit()
                else:  # Linux/Mac系统
                    # 使用libreoffice命令行工具
                    subprocess.run(['libreoffice', '--headless', '--convert-to', 'docx', '--outdir',
                                    os.path.dirname(docx_temp_file_path), temp_file_path],
                                   check=True)

                # 加载转换后的docx文件
                from langchain_community.document_loaders import Docx2txtLoader
                loader = Docx2txtLoader(docx_temp_file_path)

            except Exception as e:
                # 如果转换失败，尝试提取文本内容
                print(f"转换.doc文件失败: {str(e)}")
                print("尝试直接提取文本内容...")

                # 创建临时txt文件路径
                txt_temp_file_path = os.path.splitext(temp_file_path)[0] + '.txt'

                # 尝试提取文本内容
                try:
                    if os.name == 'nt':  # Windows系统
                        # 使用win32com提取文本
                        import win32com.client
                        word = win32com.client.Dispatch("Word.Application")
                        doc = word.Documents.Open(temp_file_path)
                        text = doc.Content.Text
                        doc.Close()
                        word.Quit()

                        # 保存为txt文件
                        with open(txt_temp_file_path, 'w', encoding='utf-8') as f:
                            f.write(text)
                    else:  # Linux/Mac系统
                        # 使用antiword提取文本
                        result = subprocess.run(['antiword', temp_file_path], capture_output=True, text=True)
                        text = result.stdout

                        # 保存为txt文件
                        with open(txt_temp_file_path, 'w', encoding='utf-8') as f:
                            f.write(text)

                    # 加载txt文件
                    from langchain_community.document_loaders import TextLoader
                    loader = TextLoader(txt_temp_file_path, encoding='utf-8')

                except Exception as e2:
                    raise ValueError(f"无法处理.doc文件: {str(e2)}")

        elif ext == '.txt':
            # 检测文本文件编码
            with open(temp_file_path, 'rb') as f:
                raw_data = f.read(1024)  # 读取前1024字节用于编码检测
                result = chardet.detect(raw_data)
                encoding = result['encoding'] or 'utf-8'
            from langchain_community.document_loaders import TextLoader
            loader = TextLoader(temp_file_path, encoding=encoding)
        elif ext == '.csv':
            from langchain_community.document_loaders import CSVLoader
            # 使用UnstructuredCSVLoader可以更好地处理复杂的CSV文件
            loader = CSVLoader(
                file_path=temp_file_path,
                encoding='utf-8',
                csv_args={
                    'delimiter': ',',
                    'quotechar': '"',
                    'fieldnames': None
                }
            )
        elif ext == '.xlsx':
            from langchain_community.document_loaders import UnstructuredExcelLoader
            # 使用UnstructuredExcelLoader处理xlsx文件
            loader = UnstructuredExcelLoader(
                temp_file_path,
                mode="elements",  # 将Excel中的每个元素作为单独文档处理
                strategy="fast"  # 快速模式，也可以选择"hi_res"获取更高精度
            )
        elif ext == '.html' or ext == '.htm':
            from langchain_community.document_loaders import WebBaseLoader
            loader = WebBaseLoader(f"file://{temp_file_path}")
        else:
            raise ValueError(f"不支持的文件类型: {ext}")

        # 加载文档
        documents = loader.load()
        return documents

    except Exception as e:
        # 记录详细的错误信息
        error_msg = f"文件加载失败: {str(e)}"
        print(error_msg)
        raise  # 重新抛出异常，让调用者处理

    finally:
        # 清理临时文件
        try:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                print(f"已清理临时文件: {temp_file_path}")

            # 清理可能生成的临时docx或txt文件
            docx_temp_file_path = os.path.splitext(temp_file_path)[0] + '.docx'
            if os.path.exists(docx_temp_file_path):
                os.remove(docx_temp_file_path)
                print(f"已清理临时文件: {docx_temp_file_path}")

            txt_temp_file_path = os.path.splitext(temp_file_path)[0] + '.txt'
            if os.path.exists(txt_temp_file_path):
                os.remove(txt_temp_file_path)
                print(f"已清理临时文件: {txt_temp_file_path}")

        except Exception as e:
            print(f"清理临时文件失败: {str(e)}")


if __name__ == '__main__':
    # 测试CSV文件
    csv_file_path = "C:\\Users\\huang\\Desktop\\test.csv"


    class MockFile:
        def __init__(self, file_path):
            self.file_path = file_path
            self.filename = os.path.basename(file_path)

        def save(self, temp_path):
            shutil.copy2(self.file_path, temp_path)


    # 测试CSV文件
    print("\n测试CSV文件:")
    mock_csv_file = MockFile(csv_file_path)
    try:
        docs = load_docs(mock_csv_file)
        if isinstance(docs, list) and len(docs) > 0:
            print(f"成功加载 {len(docs)} 个文档片段")
            for i, doc in enumerate(docs[:3], 1):
                print(f"\n文档片段 {i}:")
                print(doc.page_content[:200] + "...")
        else:
            print("未加载到任何文档内容")
    except Exception as e:
        print(f"操作失败: {str(e)}")

    # 测试XLSX文件
    xlsx_file_path = "C:\\Users\\huang\\Desktop\\test.xlsx"
    print("\n测试XLSX文件:")
    mock_xlsx_file = MockFile(xlsx_file_path)
    try:
        docs = load_docs(mock_xlsx_file)
        if isinstance(docs, list) and len(docs) > 0:
            print(f"成功加载 {len(docs)} 个文档片段")
            for i, doc in enumerate(docs[:3], 1):
                print(f"\n文档片段 {i}:")
                print(doc.page_content[:200] + "...")
        else:
            print("未加载到任何文档内容")
    except Exception as e:
        print(f"操作失败: {str(e)}")