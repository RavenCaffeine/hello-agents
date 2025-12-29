import ast
import math
import re

from dotenv import load_dotenv
# 加载 .env 文件中的环境变量
load_dotenv()

import os
from serpapi import SerpApiClient
from typing import Dict, Any

def search(query: str) -> str:
    """
    一个基于SerpApi的实战网页搜索引擎工具。
    它会智能地解析搜索结果，优先返回直接答案或知识图谱信息。
    """
    print(f"🔍 正在执行 [SerpApi] 网页搜索: {query}")
    try:
        api_key = os.getenv("SERPAPI_API_KEY")
        if not api_key:
            return "错误：SERPAPI_API_KEY 未在 .env 文件中配置。"

        params = {
            "engine": "google",
            "q": query,
            "api_key": api_key,
            "gl": "cn",  # 国家代码
            "hl": "zh-cn", # 语言代码
        }
        
        client = SerpApiClient(params)
        results = client.get_dict()
        
        # 智能解析：优先寻找最直接的答案
        if "answer_box_list" in results:
            return "\n".join(results["answer_box_list"])
        if "answer_box" in results and "answer" in results["answer_box"]:
            return results["answer_box"]["answer"]
        if "knowledge_graph" in results and "description" in results["knowledge_graph"]:
            return results["knowledge_graph"]["description"]
        if "organic_results" in results and results["organic_results"]:
            # 如果没有直接答案，则返回前三个有机结果的摘要
            snippets = [
                f"[{i+1}] {res.get('title', '')}\n{res.get('snippet', '')}"
                for i, res in enumerate(results["organic_results"][:3])
            ]
            return "\n\n".join(snippets)
        
        return f"对不起，没有找到关于 '{query}' 的信息。"

    except Exception as e:
        return f"搜索时发生错误: {e}"

    # -------------------------- 新增：计算器工具实现 --------------------------
def calculator(expression: str) -> str:
    """
    安全的数学计算器工具，支持加减乘除、括号、幂运算（^）、基础数学函数
    """
    print(f"🧮 正在执行 [Calculator] 数学计算: {expression}")
    try:
        # ========== 新增：替换中文运算符 ==========
        # 把中文乘除号替换为Python识别的*/
        expr_clean = expression.replace("×", "*").replace("÷", "/")

        # 1. 输入安全校验：仅允许数字、运算符、括号、小数点、math函数
        allowed_pattern = re.compile(r'^[0-9\+\-\*\/\(\)\.\^ \t]+(?:math\.[a-zA-Z_]+)*$')
        if not allowed_pattern.match(expr_clean.strip()):  # 校验替换后的表达式
            return "错误：输入包含非法字符！仅支持数字、+-*/()^. 和math模块基础函数（如math.sqrt）。"

        # 2. 兼容幂运算写法（^ → **）
        safe_expr = expr_clean.strip().replace("^", "**")  # 基于替换后的表达式处理

        # 后续逻辑不变...
        # 3. 语法校验
        try:
            ast.parse(safe_expr, mode='eval')
        except SyntaxError as e:
            return f"错误：表达式语法错误 → {str(e)}"

        # 4. 安全执行计算
        allowed_context = {
            "math": math,
            "abs": abs,
            "pow": pow,
            "sqrt": math.sqrt,
            "sin": math.sin,
            "cos": math.cos,
            "log": math.log
        }
        result = eval(safe_expr, {"__builtins__": None}, allowed_context)

        # 5. 格式化结果（可选：显示原始输入，更友好）
        if isinstance(result, float):
            # 同时显示原始输入和实际执行的表达式
            return f"计算结果：{expression} = {result:.4f}（实际执行：{safe_expr}）"
        else:
            return f"计算结果：{expression} = {result}（实际执行：{safe_expr}）"

    except ZeroDivisionError:
        return "错误：除数不能为0！"
    except NameError as e:
        return f"错误：未知函数 → {str(e)}（仅支持math模块基础函数）"
    except Exception as e:
        return f"计算错误: {str(e)}"


from typing import Dict, Any

class ToolExecutor:
    """
    一个工具执行器，负责管理和执行工具。
    """
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}

    def registerTool(self, name: str, description: str, func: callable):
        """
        向工具箱中注册一个新工具。
        """
        if name in self.tools:
            print(f"警告：工具 '{name}' 已存在，将被覆盖。")
        
        self.tools[name] = {"description": description, "func": func}
        print(f"工具 '{name}' 已注册。")

    def getTool(self, name: str) -> callable:
        """
        根据名称获取一个工具的执行函数。
        """
        return self.tools.get(name, {}).get("func")

    def getAvailableTools(self) -> str:
        """
        获取所有可用工具的格式化描述字符串。
        """
        return "\n".join([
            f"- {name}: {info['description']}" 
            for name, info in self.tools.items()
        ])


# --- 工具初始化与使用示例 ---
if __name__ == '__main__':
    # 1. 初始化工具执行器
    toolExecutor = ToolExecutor()

    # 2. 注册我们的实战搜索工具
    search_description = "一个网页搜索引擎。当你需要回答关于时事、事实以及在你的知识库中找不到的信息时，应使用此工具。"
    toolExecutor.registerTool("Search", search_description, search)
    
    # 3. 打印可用的工具
    print("\n--- 可用的工具 ---")
    print(toolExecutor.getAvailableTools())

    # 4. 智能体的Action调用，这次我们问一个实时性的问题
    print("\n--- 执行 Action: Search['英伟达最新的GPU型号是什么'] ---")
    tool_name = "Search"
    tool_input = "英伟达最新的GPU型号是什么"

    tool_function = toolExecutor.getTool(tool_name)
    if tool_function:
        observation = tool_function(tool_input)
        print("--- 观察 (Observation) ---")
        print(observation)
    else:
        print(f"错误：未找到名为 '{tool_name}' 的工具。")
