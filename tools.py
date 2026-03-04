import os

def read_file(filepath):
    """读取文件内容"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"读取文件失败: {e}"

def write_file(filepath, content):
    """写入文件内容"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"成功写入文件: {filepath}"
    except Exception as e:
        return f"写入文件失败: {e}"

def list_files(directory="."):
    """列出目录文件"""
    try:
        files = os.listdir(directory)
        return "\n".join(files)
    except Exception as e:
        return f"列出文件失败: {e}"
