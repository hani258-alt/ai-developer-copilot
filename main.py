from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
import os

load_dotenv()

if __name__ == "__main__":
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    api_base = os.environ.get("DEEPSEEK_API_BASE", "")
    model = os.environ.get("DEEPSEEK_MODEL", "deepseek-v3")

    print(f"API Key 已检测到 (前8位: {api_key[:8]}...)")
    print(f"模型: {model}")
    print(f"API地址: {api_base}")

    llm = ChatDeepSeek(model=model)
    resp = llm.invoke("你好，请简短回复连接成功四个字。")
    print(f"响应: {resp.content}")
