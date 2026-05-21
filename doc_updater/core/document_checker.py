from typing import Dict, List, Any, Optional
from formats import XlsxHandler


class DocumentChecker:
    """文档完整性检查器"""

    class ValidationError:
        """验证错误对象"""
        def __init__(self, sheet_name: str, row: int, col: int, column_name: str, description: str):
            self.sheet_name = sheet_name
            self.row = row
            self.col = col
            self.column_name = column_name
            self.description = description

        def to_dict(self) -> Dict[str, Any]:
            return {
                'sheet_name': self.sheet_name,
                'row': self.row,
                'col': self.col,
                'column_name': self.column_name,
                'description': self.description
            }

        def __str__(self) -> str:
            if self.column_name:
                return f"工作表: {self.sheet_name}, 行: {self.row}, 列: {self.column_name}, 错误: {self.description}"
            else:
                return f"工作表: {self.sheet_name}, 行: {self.row}, 错误: {self.description}"

    def __init__(self):
        self.errors = []

    def check_input_document(self, file_path: str) -> tuple[bool, List[ValidationError]]:
        """
        检查输入文档的完整性

        检查内容: E列（列标题为"打点结果"）所有单元格不为空

        Returns:
            (是否通过检查, 错误列表)
        """
        self.errors = []
        handler = XlsxHandler()

        if not handler.read(file_path):
            error = self.ValidationError(
                sheet_name="",
                row=0,
                col=0,
                column_name="",
                description="无法读取SWRT输入文档文件"
            )
            self.errors.append(error)
            return False, self.errors

        for sheet_idx, sheet_data in enumerate(handler.data):
            sheet_name = sheet_data['sheet_name']
            rows = sheet_data['rows']

            if len(rows) < 2:
                continue

            header_row = rows[0]
            data_rows = rows[1:]

            col_e_index = -1
            col_e_name = ""

            for idx, header in enumerate(header_row):
                header_str = str(header).strip() if header else ""
                if "打点结果" in header_str or header_str.upper() in ['E', 'E列']:
                    col_e_index = idx
                    col_e_name = header_str if header_str else "E列"
                    break

            if col_e_index == -1:
                continue

            for row_idx, row in enumerate(data_rows):
                cell_value = None
                if col_e_index < len(row):
                    cell_value = row[col_e_index]

                if cell_value is None or str(cell_value).strip() == "":
                    error = self.ValidationError(
                        sheet_name=sheet_name,
                        row=row_idx + 2,
                        col=col_e_index + 1,
                        column_name=col_e_name,
                        description="单元格为空"
                    )
                    self.errors.append(error)

        return len(self.errors) == 0, self.errors

    def check_platform_document(self, file_path: str) -> tuple[bool, List[ValidationError]]:
        """
        检查平台文档的完整性

        检查内容: P列（列标题为"适用范围"）所有单元格不为空

        Returns:
            (是否通过检查, 错误列表)
        """
        self.errors = []
        handler = XlsxHandler()

        if not handler.read(file_path):
            error = self.ValidationError(
                sheet_name="",
                row=0,
                col=0,
                column_name="",
                description="无法读取SWRT平台文档文件"
            )
            self.errors.append(error)
            return False, self.errors

        for sheet_idx, sheet_data in enumerate(handler.data):
            sheet_name = sheet_data['sheet_name']
            rows = sheet_data['rows']

            if len(rows) < 2:
                continue

            header_row = rows[0]
            data_rows = rows[1:]

            col_p_index = -1
            col_p_name = ""

            for idx, header in enumerate(header_row):
                header_str = str(header).strip() if header else ""
                if "适用范围" in header_str or header_str.upper() in ['P', 'P列']:
                    col_p_index = idx
                    col_p_name = header_str if header_str else "P列"
                    break

            if col_p_index == -1:
                continue

            for row_idx, row in enumerate(data_rows):
                cell_value = None
                if col_p_index < len(row):
                    cell_value = row[col_p_index]

                if cell_value is None or str(cell_value).strip() == "":
                    error = self.ValidationError(
                        sheet_name=sheet_name,
                        row=row_idx + 2,
                        col=col_p_index + 1,
                        column_name=col_p_name,
                        description="单元格为空"
                    )
                    self.errors.append(error)

        return len(self.errors) == 0, self.errors

    @staticmethod
    def format_errors_for_display(errors: List[ValidationError]) -> str:
        """将错误列表格式化为可读文本"""
        if not errors:
            return "文档检查通过，没有发现错误。"

        result = f"共发现 {len(errors)} 个错误:\n\n"

        for i, error in enumerate(errors, 1):
            result += f"  {i}. {str(error)}\n"

        return result

    @staticmethod
    def get_error_count_by_type(errors: List[ValidationError]) -> dict:
        """统计错误分布"""
        sheet_stats = {}
        for error in errors:
            sheet = error.sheet_name or "未知工作表"
            if sheet not in sheet_stats:
                sheet_stats[sheet] = 0
            sheet_stats[sheet] += 1
        return sheet_stats
