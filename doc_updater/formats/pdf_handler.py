import pdfplumber
from typing import List, Dict, Any, Tuple

class PdfHandler:
    def __init__(self):
        self.pdf = None
        self.pages = []
        self.text_content = []

    def read(self, file_path: str) -> bool:
        try:
            self.pdf = pdfplumber.open(file_path)
            self._parse_pdf()
            return True
        except Exception as e:
            print(f"读取PDF文件失败: {e}")
            return False

    def _parse_pdf(self):
        self.pages = []
        self.text_content = []

        if self.pdf:
            for page_num, page in enumerate(self.pdf.pages):
                page_data = {
                    'page_num': page_num + 1,
                    'text': page.extract_text() or '',
                    'tables': page.extract_tables() or []
                }
                self.pages.append(page_data)
                self.text_content.append(page_data['text'])

    def get_all_text(self) -> str:
        return '\n\n'.join(self.text_content)

    def get_page_text(self, page_num: int) -> str:
        if 0 < page_num <= len(self.pages):
            return self.pages[page_num - 1]['text']
        return ''

    def get_page_count(self) -> int:
        return len(self.pages) if self.pdf else 0

    def get_tables(self, page_num: int = None) -> List[List[List[str]]]:
        if page_num:
            if 0 < page_num <= len(self.pages):
                return self.pages[page_num - 1]['tables']
        else:
            all_tables = []
            for page in self.pages:
                all_tables.extend(page['tables'])
            return all_tables
        return []

    def find_text(self, search_text: str) -> List[Tuple[int, str]]:
        matches = []
        for page_data in self.pages:
            if search_text in page_data['text']:
                matches.append((page_data['page_num'], page_data['text']))
        return matches

    def extract_text_by_blocks(self) -> List[Dict[str, Any]]:
        blocks = []
        for page_data in self.pages:
            text = page_data['text']
            if text:
                lines = text.split('\n')
                for line in lines:
                    if line.strip():
                        blocks.append({
                            'page': page_data['page_num'],
                            'text': line.strip()
                        })
        return blocks

    def close(self):
        if self.pdf:
            self.pdf.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
