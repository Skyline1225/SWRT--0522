from typing import List, Dict, Any, Tuple
import re

class TxtHandler:
    def __init__(self):
        self.content = ''
        self.lines = []
        self.file_path = None

    def read(self, file_path: str) -> bool:
        try:
            self.file_path = file_path
            with open(file_path, 'r', encoding='utf-8') as f:
                self.content = f.read()
            self.lines = self.content.split('\n')
            return True
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    self.content = f.read()
                self.lines = self.content.split('\n')
                return True
            except Exception as e:
                print(f"读取文本文件失败: {e}")
                return False
        except Exception as e:
            print(f"读取文本文件失败: {e}")
            return False

    def get_all_text(self) -> str:
        return self.content

    def get_lines(self) -> List[str]:
        return self.lines

    def get_line(self, line_num: int) -> str:
        if 0 <= line_num < len(self.lines):
            return self.lines[line_num]
        return ''

    def find_text(self, search_text: str) -> List[Tuple[int, str]]:
        matches = []
        for idx, line in enumerate(self.lines):
            if search_text in line:
                matches.append((idx, line))
        return matches

    def replace_text(self, old_text: str, new_text: str) -> int:
        count = self.content.count(old_text)
        self.content = self.content.replace(old_text, new_text)
        self.lines = self.content.split('\n')
        return count

    def update_line(self, line_num: int, new_text: str) -> bool:
        if 0 <= line_num < len(self.lines):
            self.lines[line_num] = new_text
            self.content = '\n'.join(self.lines)
            return True
        return False

    def save(self, output_path: str) -> bool:
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(self.content)
            return True
        except Exception as e:
            print(f"保存文本文件失败: {e}")
            return False

    def insert_line(self, line_num: int, new_text: str) -> bool:
        if 0 <= line_num <= len(self.lines):
            self.lines.insert(line_num, new_text)
            self.content = '\n'.join(self.lines)
            return True
        return False

    def delete_line(self, line_num: int) -> bool:
        if 0 <= line_num < len(self.lines):
            del self.lines[line_num]
            self.content = '\n'.join(self.lines)
            return True
        return False

    def get_statistics(self) -> Dict[str, Any]:
        return {
            'total_lines': len(self.lines),
            'total_chars': len(self.content),
            'non_empty_lines': sum(1 for line in self.lines if line.strip())
        }
