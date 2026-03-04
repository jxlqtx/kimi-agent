import os
import json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class KimiAgent:
    def __init__(self, model="moonshot-v1-8k"):
        self.client = OpenAI(
            api_key=os.getenv("KIMI_API_KEY"),
            base_url=os.getenv("KIMI_BASE_URL")
        )
        self.model = model
        self.conversation_history = []
        self.system_prompt = """你是 Kimi，一个有帮助的 AI 助手。
当前时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
你可以：
1. 回答问题和提供建议
2. 读取和写入本地文件
3. 记住对话上下文"""

    def chat(self, message, stream=True):
        """发送消息并获取回复"""
        # 添加用户消息到历史
        self.conversation_history.append({"role": "user", "content": message})
        
        # 构建完整消息列表
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.conversation_history[-10:])  # 保留最近10轮
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=stream
            )
            
            full_response = ""
            if stream:
                print("Kimi: ", end="", flush=True)
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        print(content, end="", flush=True)
                        full_response += content
                print()
            else:
                full_response = response.choices[0].message.content
                print(f"Kimi: {full_response}")
            
            # 添加助手回复到历史
            self.conversation_history.append({"role": "assistant", "content": full_response})
            return full_response
            
        except Exception as e:
            print(f"错误: {e}")
            return None

    def save_conversation(self, filename="conversation.json"):
        """保存对话历史"""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)
        print(f"对话已保存到 {filename}")

    def load_conversation(self, filename="conversation.json"):
        """加载对话历史"""
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                self.conversation_history = json.load(f)
            print(f"已加载 {len(self.conversation_history)} 条历史消息")
        else:
            print("没有找到历史对话文件")

    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []
        print("对话历史已清空")

def main():
    agent = KimiAgent()
    
    print("=" * 50)
    print("🤖 Kimi 智能体已启动")
    print("命令: /save 保存对话 | /load 加载对话 | /clear 清空历史 | /quit 退出")
    print("=" * 50)
    
    while True:
        try:
            user_input = input("\n你: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['/quit', '/exit', 'quit', 'exit']:
                print("再见！")
                break
            elif user_input.lower() == '/save':
                agent.save_conversation()
            elif user_input.lower() == '/load':
                agent.load_conversation()
            elif user_input.lower() == '/clear':
                agent.clear_history()
            else:
                agent.chat(user_input)
                
        except KeyboardInterrupt:
            print("\n再见！")
            break
        except Exception as e:
            print(f"错误: {e}")

if __name__ == "__main__":
    main()
