import os
import shutil
from typing import Optional

def get_file_extension(file_path: str) -> str:
    return os.path.splitext(file_path)[1].lower().lstrip('.')

def is_supported_file(file_path: str) -> bool:
    from config.settings import Settings
    ext = get_file_extension(file_path)
    return ext in Settings.SUPPORTED_FORMATS

def get_file_name(file_path: str) -> str:
    return os.path.basename(file_path)

def get_file_name_without_ext(file_path: str) -> str:
    return os.path.splitext(os.path.basename(file_path))[0]

def ensure_dir(dir_path: str) -> None:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def copy_file(src: str, dst: str) -> None:
    shutil.copy2(src, dst)

def read_file_safe(file_path: str, encoding: str = 'utf-8') -> Optional[str]:
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='gbk') as f:
                return f.read()
        except Exception:
            return None
    except Exception:
        return None

def write_file_safe(file_path: str, content: str, encoding: str = 'utf-8') -> bool:
    try:
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        return True
    except Exception:
        return False
