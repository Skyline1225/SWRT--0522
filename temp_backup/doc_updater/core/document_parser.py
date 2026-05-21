from typing import Dict, List, Any, Optional
from formats import XlsxHandler, DocxHandler, PdfHandler, TxtHandler
from config import Settings, DocumentType
from utils import get_file_extension

class DocumentParser:
    def __init__(self):
        self.handlers = {
            'xlsx': XlsxHandler(),
            'xls': XlsxHandler(),
            'docx': DocxHandler(),
            'pdf': PdfHandler(),
            'txt': TxtHandler()
        }
        self.current_handler = None
        self.file_path = None
        self.file_type = None

    def read_document(self, file_path: str, doc_type: str = None) -> bool:
        ext = get_file_extension(file_path)

        if ext not in self.handlers:
            print(f"不支持的文件格式: {ext}")
            return False

        self.file_path = file_path
        self.file_type = doc_type
        self.current_handler = self.handlers.get(ext)

        if self.current_handler:
            return self.current_handler.read(file_path)
        return False

    def get_all_text(self) -> str:
        if self.current_handler:
            return self.current_handler.get_all_text()
        return ''

    def get_all_data(self) -> List[List[Any]]:
        if isinstance(self.current_handler, XlsxHandler):
            return self.current_handler.get_all_values()
        elif isinstance(self.current_handler, (DocxHandler, PdfHandler, TxtHandler)):
            return [[line] for line in self.current_handler.get_all_text().split('\n')]
        return []

    def get_structure(self) -> Dict[str, Any]:
        if not self.current_handler:
            return {}

        if isinstance(self.current_handler, XlsxHandler):
            return {
                'type': 'xlsx',
                'sheets': self.current_handler.sheet_names,
                'dimensions': self.current_handler.get_dimensions()
            }
        elif isinstance(self.current_handler, DocxHandler):
            return {
                'type': 'docx',
                'paragraphs': len(self.current_handler.paragraphs),
                'tables': len(self.current_handler.tables)
            }
        elif isinstance(self.current_handler, PdfHandler):
            return {
                'type': 'pdf',
                'pages': self.current_handler.get_page_count()
            }
        elif isinstance(self.current_handler, TxtHandler):
            return {
                'type': 'txt',
                'lines': len(self.current_handler.lines),
                'statistics': self.current_handler.get_statistics()
            }
        return {}

    def find_content(self, search_text: str) -> List[Dict[str, Any]]:
        if not self.current_handler:
            return []

        results = []
        if isinstance(self.current_handler, XlsxHandler):
            matches = self.current_handler.find_matching_cells(search_text)
            for sheet_idx, row, col, value in matches:
                results.append({
                    'type': 'cell',
                    'sheet': sheet_idx,
                    'row': row,
                    'col': col,
                    'value': value,
                    'location': f"Sheet{sheet_idx+1} Row{row+1} Col{col+1}"
                })
        else:
            matches = self.current_handler.find_text(search_text)
            for idx, text in matches:
                results.append({
                    'type': 'text',
                    'index': idx,
                    'text': text,
                    'location': f"Line/Index {idx+1}"
                })
        return results

    def update_content(self, location: Dict[str, Any], new_value: str) -> bool:
        if not self.current_handler:
            return False

        if isinstance(self.current_handler, XlsxHandler):
            sheet_idx = location.get('sheet', 0)
            row = location.get('row', 0)
            col = location.get('col', 0)
            return self.current_handler.set_cell_value(sheet_idx, row, col, new_value)
        elif isinstance(self.current_handler, (DocxHandler, TxtHandler)):
            index = location.get('index', 0)
            if isinstance(self.current_handler, DocxHandler):
                return self.current_handler.update_paragraph(index, new_value)
            else:
                return self.current_handler.update_line(index, new_value)
        return False

    def save_document(self, output_path: str) -> bool:
        if self.current_handler:
            return self.current_handler.save(output_path)
        return False

    def get_preview_data(self, max_rows: int = 100) -> List[List[Any]]:
        data = self.get_all_data()
        return data[:max_rows]
