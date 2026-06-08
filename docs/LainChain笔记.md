# 🦜️ LangChain 入门笔记

## 1. 它是什么？

LangChain 是一个**把大语言模型（LLM，如 DeepSeek）包装成“应用积木”的 Python 库**。
它的目的是让你像搭乐高一样，把“模型调用”、“提示词”、“记忆”、“外部工具”组合成复杂 AI 应用。

------

## 2.创建项目与环境（初始化）

### 第一步：

![image-20260507202628277](C:\Users\th\AppData\Roaming\Typora\typora-user-images\image-20260507202628277.png)

### 第二步：

### 在终端初始化 —— `uv init` 再 `uv add`

bash

```bash
uv init                  # 让当前目录变成一个 Python 项目
uv add langchain langchain-deepseek
```



- **效果**：`uv init` 会生成几个文件，最重要的是 **`pyproject.toml`******（Python 项目的“说明书”）。****
  然后 `uv add` 会在安装包的同时，把依赖的包名和版本自动写进 `pyproject.toml`。
- **背后发生了什么**：
  1. 生成了 `pyproject.toml`、`README.md`、`.python-version` 等文件。
  2. `uv add` 不仅装包，还会更新 `pyproject.toml` 里的 `[project] dependencies` 列表，并生成/更新 `uv.lock` 锁文件（锁定精确版本）。
- **适用场景**：要长期维护的项目、需要和同事协作、想精确复现环境（比如用 `uv sync` 一键还原）、想发版到 PyPI。
- **优点**：依赖被明确记录，其他人只用 `uv sync` 就能装出一模一样的环境，不会出现“我这里能跑，你那里不行”。

------



## 3.访问模型：

![image-20260507204744930](C:\Users\th\AppData\Roaming\Typora\typora-user-images\image-20260507204744930.png)

















































## 3. 第一个可运行代码（解决你刚才的报错）



```python
import os
import getpass

# 安全输入API Key（终端里不会显示）
os.environ["DEEPSEEK_API_KEY"] = getpass.getpass("🔑 请输入你的DeepSeek API Key")

from langchain.chat_models import init_chat_model

# 创建模型实例（最简形式）
model = init_chat_model(model="deepseek-chat")

# 调用模型
response = model.invoke("用一句话解释什么是LangChain")
print(response.content)
```



> ✅ 导入路径全部小写：`langchain.chat_models`
> ✅ 函数名完整：`init_chat_model`，不是 `init_cl`
> ✅ 必须先设置环境变量 `DEEPSEEK_API_KEY`

------

## 4. 核心概念地图

LangChain 整个框架围绕这几个“积木”：

| 概念                | 作用                                             | 你刚用到的                     |
| :------------------ | :----------------------------------------------- | :----------------------------- |
| **Model（模型）**   | 直接调用大语言模型                               | `init_chat_model` 就是模型入口 |
| **Prompt Template** | 把你的输入包装成高质量提示词                     | 还没用，马上会                 |
| **Chain（链）**     | 把模型、提示词、输出处理等串成流水线             | 核心精髓                       |
| **Output Parser**   | 把模型的原始文本变成结构化的数据（JSON、列表等） | 进阶必学                       |
| **Memory**          | 让对话能“记住”历史                               | 多轮对话专用                   |

------

## 5. 常用核心组件快速上手

### 5.1 模型 (Model) 的参数调优

你问过的 `init_chat_model` 常用参数一览：

python

```python
model = init_chat_model(
    model="deepseek-chat",
    temperature=0.7,     # 0=严谨, 1=创意, 默认0.7左右
    max_tokens=200,      # 限制回复长度，控制成本
    streaming=False,     # True = 打字机效果实时输出（流式输出）
    timeout=30,          # 超时秒数
)
```



> 💡 最佳实践：**从 `temperature=0.0` 开始调试**，稳定后再调大追求创意。

### 5.2 提示模板 (Prompt Template)

别把问题直接扔给模型，用模板写更规范的提示词。

[^LangChain的提示模板：帮你把不固定的变量，填入一个设计好的固定结构里。它负责的是“格式和流程”。]: 所以好的提示词很重要

```python
from langchain.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个{role}，用{lang}回答问题。"),
    ("user", "{input}")
])

# 生成带角色和语言参数的提示词
formatted = prompt.format(role="物理学家", lang="中文", input="什么是黑洞")
# formatted 现在是：
# System: 你是一个物理学家，用中文回答问题。
# Human: 什么是黑洞
```



### 5.3 链 (Chain) — 最核心的积木

链把“提示词 + 模型 + 输出”串起来。

python

```python
from langchain.chat_models import init_chat_model
from langchain.prompts import ChatPromptTemplate

model = init_chat_model(model="deepseek-chat")
prompt = ChatPromptTemplate.from_messages([
    ("system", "将以下英文翻译成{target_lang}。"),
    ("user", "{text}")
])

# 用 LCEL（LangChain表达式语言）构建链
chain = prompt | model

# 调用链：传参 → 自动注入模板 → 调用模型
response = chain.invoke({
    "target_lang": "法语",
    "text": "Hello, how are you?"
})
print(response.content)
```



### 5.4 输出解析器 (Output Parser) — 让返回结果结构化

模型返回文本，但你想直接拿到 Python 字典，用解析器。

python

```python
from langchain.output_parsers import ResponseSchema, StructuredOutputParser

# 定义你想要的数据结构
schemas = [
    ResponseSchema(name="sentiment", description="情感倾向：positive, negative, neutral"),
    ResponseSchema(name="summary", description="文本的一句话说摘要"),
]
parser = StructuredOutputParser.from_response_schemas(schemas)

# 把格式说明塞进提示词
prompt = ChatPromptTemplate.from_messages([
    ("system", "分析用户文本。\n{format_instructions}"),
    ("user", "{text}")
])

chain = prompt | model | parser   # 最后一步直接出结构化数据

result = chain.invoke({
    "text": "今天天气真好，但我有点累。",
    "format_instructions": parser.get_format_instructions()
})
print(result)  # 会得到一个字典 {'sentiment': 'mixed', 'summary': '...'}
```



------

## 6. 典型“坑”汇总（你刚踩过的）

- **`ModuleNotFoundError: No module named 'langchain'`** → 当前虚拟环境没装，请在对应终端 `pip install langchain`。
- **`ImportError: cannot import name 'init_chat_model'`** → 拼写错误，检查 `from langchain.chat_models` 全小写，函数名完整。
- **`ValueError: DEEPSEEK_API_KEY must be set`** → 忘了设置 API Key，用 `os.environ` 或 `getpass` 设置。
- **PyCharm 显示红色波浪线，但运行正常** → 解释器缓存不同步，问题不大，保存文件，Reload All from Disk，或重启 PyCharm。
- **`getpass.getpass()` 永远在等待** → 它正在等你输入，输入时屏幕无显示是正常的安全特性，粘贴后按回车。

------

## 7. 学习路线建议

1. ✅ **Hello World**：用 `model.invoke("你好")` 验证通联。
2. ✅ **加提示模板**：让模型扮演某个角色完成任务。
3. ✅ **构建第一条链**：提示词 → 模型 → 输出。
4. ✅ **输出解析**：让返回直接做成可用的 Python 字典/列表。
5. 📚 **进阶**：加入 `Memory` 做多轮对话、使用 `Agent` + 工具（搜索引擎、计算器等）。