import os
import json
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class AutoAgent:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("KIMI_API_KEY"),
            base_url=os.getenv("KIMI_BASE_URL")
        )
        self.tools = {
            "read_file": self.read_file,
            "write_file": self.write_file,
            "execute_command": self.execute_command,
            "search_files": self.search_files,
            "git_commit": self.git_commit,
            "create_project": self.create_project
        }
        
    def chat(self, message):
        """处理用户指令并自动执行工具"""
        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": message}
        ]
        
        response = self.client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=messages,
            tools=self._get_tools_schema(),
            tool_choice="auto"
        )
        
        # 处理工具调用
        if response.choices[0].message.tool_calls:
            return self._handle_tool_calls(response.choices[0].message.tool_calls)
        else:
            return response.choices[0].message.content
    
    def _get_system_prompt(self):
        return """你是 AutoAgent，一个自动化助手。你可以：
1. 读取/写入文件
2. 执行系统命令
3. 搜索文件内容
4. 自动提交 Git
5. 创建项目模板

根据用户需求自动选择合适工具执行。"""
    
    def _get_tools_schema(self):
        return [
            {
                "type": "function",
                "function": {
                    "name": "execute_command",
                    "description": "执行系统命令",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {"type": "string", "description": "要执行的命令"}
                        },
                        "required": ["command"]
                    }
                }
            },
            {
                "type": "function", 
                "function": {
                    "name": "read_file",
                    "description": "读取文件内容",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "文件路径"}
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "写入文件内容",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "文件路径"},
                            "content": {"type": "string", "description": "文件内容"}
                        },
                        "required": ["path", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "git_commit",
                    "description": "自动提交 Git 更改",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "message": {"type": "string", "description": "提交信息"}
                        },
                        "required": ["message"]
                    }
                }
            }
        ]
    
    def _handle_tool_calls(self, tool_calls):
        results = []
        for call in tool_calls:
            function_name = call.function.name
            arguments = json.loads(call.function.arguments)
            
            if function_name in self.tools:
                result = self.tools[function_name](**arguments)
                results.append(f"[{function_name}] {result}")
            else:
                results.append(f"[错误] 未知工具: {function_name}")
        
        return "\n".join(results)
    
    # 工具实现
    def read_file(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"错误: {e}"
    
    def write_file(self, path, content):
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"成功写入: {path}"
        except Exception as e:
            return f"错误: {e}"
    
    def execute_command(self, command):
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=30
            )
            return result.stdout or result.stderr or "执行完成"
        except Exception as e:
            return f"错误: {e}"
    
    def search_files(self, pattern, path="."):
        matches = []
        for root, dirs, files in os.walk(path):
            for file in files:
                if pattern in file:
                    matches.append(os.path.join(root, file))
        return "\n".join(matches) if matches else "未找到匹配文件"
    
    def git_commit(self, message):
        try:
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", message], check=True)
            subprocess.run(["git", "push"], check=True)
            return f"已提交并推送: {message}"
        except Exception as e:
            return f"Git 错误: {e}"
    
    def create_project(self, name, template="basic"):
        templates = {
            "basic": {
                "main.py": "# 项目入口\nif __name__ == '__main__':\n    print('Hello World')",
                "README.md": f"# {name}\n\n项目描述",
                "requirements.txt": "# 依赖列表"
            },
            "agent": {
                "agent.py": "# AI Agent 模板\nclass Agent:\n    def run(self):\n        pass",
                "config.json": '{"model": "moonshot-v1-8k"}',
                "tools.py": "# 工具函数"
            }
        }
        
        if template not in templates:
            return f"未知模板: {template}"
        
        os.makedirs(name, exist_ok=True)
        for filename, content in templates[template].items():
            filepath = os.path.join(name, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return f"已创建项目: {name} (模板: {template})"

def main():
    agent = AutoAgent()
    print("🤖 AutoAgent 自动化模式")
    print("支持: 文件操作 | 命令执行 | Git 自动化 | 项目创建")
    print("输入 'exit' 退出\n")
    
    while True:
        try:
            user_input = input("📝 指令: ").strip()
            if user_input.lower() in ['exit', 'quit']:
                break
            
            print("⚙️  执行中...")
            result = agent.chat(user_input)
            print(f"✅ 结果:\n{result}\n")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ 错误: {e}")

if __name__ == "__main__":
    main()
