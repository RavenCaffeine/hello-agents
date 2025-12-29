# test_api.py - 单独测试魔搭 API
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url="https://api-inference.modelscope.cn/v1"
)

response = client.chat.completions.create(
    model="ZhipuAI/GLM-4.7",
    messages=[{"role": "user", "content": "你好"}]
)
print(response.choices[0].message.content)