import openpyxl
from openpyxl.utils import get_column_letter
from datetime import datetime
import os
from typing import Type, List, Union, Dict, Optional
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from io import BytesIO
import tempfile

from utils.oss_utils import save_file


def save_to_xlsx(content, filename=None, sheet_name='Sheet1', headers=None):
    """
    将输入内容整理并保存为XLSX文件，并上传到OSS

    参数:
        content: 输入内容，可以是以下格式之一:
                 - 列表的列表 (每行数据)
                 - 字典列表 (每个字典代表一行，键作为列头)
        filename: 保存的文件名 (可选)，如果不提供则自动生成
        sheet_name: 工作表名称 (默认为'Sheet1')
        headers: 列头列表 (可选)，如果content是字典列表且需要自定义列顺序

    返回:
        包含文件信息和OSS上传结果的字典
    """
    # 创建工作簿和工作表
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet_name

    # 处理不同类型的内容输入
    if isinstance(content, list) and len(content) > 0:
        if isinstance(content[0], dict):  # 字典列表
            if headers is None:
                headers = list(content[0].keys())

            # 写入表头
            ws.append(headers)

            # 写入数据
            for row in content:
                ws.append([row.get(header, '') for header in headers])

        elif isinstance(content[0], (list, tuple)):  # 列表的列表
            # 如果有提供headers，先写入headers
            if headers is not None:
                ws.append(headers)
                start_row = 2
            else:
                start_row = 1

            # 写入数据
            for row in content:
                ws.append(row)

    # 自动调整列宽
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter  # 获取列字母

        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass

        adjusted_width = (max_length + 2) * 1.2
        ws.column_dimensions[column].width = adjusted_width

    # 生成文件名（如果未提供）
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"output_{timestamp}.xlsx"
    elif not filename.endswith('.xlsx'):
        filename += '.xlsx'

    # 创建一个临时文件对象用于上传
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
        # 保存Excel文件到临时文件
        wb.save(tmp_file.name)
        tmp_file.seek(0)

        # 创建一个类似文件的对象，具有filename和content_type属性
        class FileWrapper:
            def __init__(self, file_obj, filename, content_type):
                self.file = file_obj
                self.filename = filename
                self.content_type = content_type
                self.stream = file_obj

            def read(self, *args, **kwargs):
                return self.file.read(*args, **kwargs)

            def seek(self, *args, **kwargs):
                return self.file.seek(*args, **kwargs)

            def close(self):
                return self.file.close()

        file_obj = FileWrapper(
            tmp_file,
            filename=filename,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        # 上传文件到OSS
        upload_result = save_file(file_obj)

        # 关闭并删除临时文件
        tmp_file.close()
        os.unlink(tmp_file.name)

        return {
            'filename': filename,
            'upload_result': upload_result
        }


class ExcelContentItem(BaseModel):
    pass


class SaveToExcelModel(BaseModel):
    content: Union[List[List[Union[str, int, float]]], List[Dict[str, Union[str, int, float]]]] = Field(
        ...,
        description="要保存的内容，可以是列表的列表(每行数据)或字典列表(每个字典代表一行)"
    )
    filename: Optional[str] = Field(
        None,
        description="保存的文件名(可选)，如果不提供则自动生成"
    )
    sheet_name: str = Field(
        'Sheet1',
        description="工作表名称(默认为'Sheet1')"
    )
    headers: Optional[List[str]] = Field(
        None,
        description="列头列表(可选)，如果content是字典列表且需要自定义列顺序"
    )


class ExcelSaveTool(BaseTool):
    name: str = "save_to_excel"
    description: str = "将数据保存为Excel文件并上传到OSS，支持列表数据或字典数据"
    args_schema: Type[BaseModel] = SaveToExcelModel

    def _run(
            self,
            content: Union[List[List[Union[str, int, float]]], List[Dict[str, Union[str, int, float]]]],
            filename: Optional[str] = None,
            sheet_name: str = 'Sheet1',
            headers: Optional[List[str]] = None
    ) -> dict:
        """
        将输入内容整理并保存为XLSX文件并上传到OSS

        参数:
            content: 输入内容，可以是以下格式之一:
                     - 列表的列表 (每行数据)
                     - 字典列表 (每个字典代表一行，键作为列头)
            filename: 保存的文件名 (可选)，如果不提供则自动生成
            sheet_name: 工作表名称 (默认为'Sheet1')
            headers: 列头列表 (可选)，如果content是字典列表且需要自定义列顺序

        返回:
            包含文件信息和OSS上传结果的字典
        """
        return save_to_xlsx(content, filename, sheet_name, headers)


def get_excel_tools():
    excel_save_tool = ExcelSaveTool()
    return excel_save_tool


if __name__ == '__main__':
    # 示例1: 使用字典列表
    data_dicts = [
        {"姓名": "张三", "年龄": 25, "城市": "北京"},
        {"姓名": "李四", "年龄": 30, "城市": "上海"},
        {"姓名": "王五", "年龄": 28, "城市": "广州"}
    ]
    res = save_to_xlsx(data_dicts, "人员信息.xlsx", "员工数据")
    print(res)
    # 示例2: 使用列表的列表
    data_lists = [
        ["产品", "价格", "库存"],
        ["手机", 2999, 100],
        ["电脑", 5999, 50],
        ["平板", 1999, 80]
    ]
    save_to_xlsx(data_lists, "产品库存.xlsx")
