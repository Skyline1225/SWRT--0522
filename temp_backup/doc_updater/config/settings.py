import os

class Settings:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    SUPPORTED_FORMATS = {
        'docx': 'Word文档 (*.docx)',
        'xlsx': 'Excel工作簿 (*.xlsx)',
        'pdf': 'PDF文档 (*.pdf)',
        'txt': '文本文件 (*.txt)',
        'xls': 'Excel 97-2003工作簿 (*.xls)'
    }

    EXPORT_DIR = os.path.join(BASE_DIR, 'exports')
    TEMP_DIR = os.path.join(BASE_DIR, 'temp')

    MATCH_THRESHOLD = 0.75
    BATCH_SIZE = 100

    UI_WINDOW_WIDTH = 1200
    UI_WINDOW_HEIGHT = 800

    @classmethod
    def ensure_dirs(cls):
        for dir_path in [cls.EXPORT_DIR, cls.TEMP_DIR]:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

class DocumentType:
    INPUT = 'input'
    PLATFORM = 'platform'

class ChangeType:
    ADD = 'add'
    MODIFY = 'modify'
    DELETE = 'delete'
    NONE = 'none'
